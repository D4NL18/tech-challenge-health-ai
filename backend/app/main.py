"""
==================================================================================================
ARQUIVO: main.py (ENTRYPOINT DO BACKEND)
==================================================================================================
Objetivo:
Este é o ponto de entrada principal (Entrypoint) da aplicação backend, construída com o framework FastAPI.
Aqui defino o servidor HTTP, configuro a segurança (CORS e Rate Limiter Exponencial), anexo as rotas
e gerencio o "Ciclo de Vida" (Lifespan) da aplicação (para carregar modelos pesados na RAM).

Decisão Arquitetural:
Escolhi o FastAPI porque ele é assíncrono por padrão (ASGI), excelente para serviços que precisam
esperar chamadas de rede lentas (como as requisições para APIs de LLM externas, Gemini/OpenAI).
==================================================================================================
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from contextlib import asynccontextmanager
import time
from collections import defaultdict

from app.api.routers import anamnesis, admin
from app.services.inference import inference_service

class AdvancedExponentialRateLimiter(BaseHTTPMiddleware):
    """
    ----------------------------------------------------------------------------------------------
    CLASSE: AdvancedExponentialRateLimiter
    Objetivo: Proteger o Cloud Run contra ataques de DDoS e abuso de API que podem gerar custos.
    Lógica: Rastreia requisições por IP na memória. Permite 5 requisições por minuto.
    Se o IP ultrapassar, recebe um cooldown. Se tentar acessar durante o cooldown, a punição
    dobra de forma exponencial (1min -> 2min -> 4min -> 8min).
    ----------------------------------------------------------------------------------------------
    """
    def __init__(self, app: FastAPI, max_requests: int = 5, window_seconds: int = 60):
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        
        # Dicionário em memória: IP -> Estado do Usuário
        self.clients = defaultdict(lambda: {"requests": [], "blocked_until": 0, "penalties": 0})
        
    async def dispatch(self, request: Request, call_next):
        # Ignora rate limit para a rota de health check raiz para não bloquear o Load Balancer do GCP
        if request.url.path == "/":
            return await call_next(request)
            
        client_ip = request.client.host if request.client else "unknown"
        now = time.time()
        client_data = self.clients[client_ip]
        
        # 1. Verifica se o usuário já está cumprindo suspensão
        if now < client_data["blocked_until"]:
            remaining_time = int(client_data["blocked_until"] - now)
            return JSONResponse(
                status_code=429, 
                content={"error": f"Rate limit excedido. Aguarde {remaining_time} segundos."}
            )
            
        # 2. Limpa o histórico de requisições que já saíram da janela de 1 minuto
        client_data["requests"] = [req for req in client_data["requests"] if req > now - self.window_seconds]
        
        # 3. Verifica se atingiu o limite de requisições permitidas (Gatilho inicial)
        if len(client_data["requests"]) >= self.max_requests:
            client_data["penalties"] += 1
            # Limita a punição máxima a 1 hora (3600 segundos) para não ser infinito
            block_time = min(self.window_seconds * (2 ** (client_data["penalties"] - 1)), 3600)
            client_data["blocked_until"] = now + block_time
            
            return JSONResponse(
                status_code=429, 
                content={"error": f"Rate limit excedido. Muitas requisições. IP bloqueado por {block_time} segundos."}
            )
            
        # 4. Registra a requisição atual como permitida
        client_data["requests"].append(now)
        
        # Passa a requisição para frente
        response = await call_next(request)
        return response

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    ----------------------------------------------------------------------------------------------
    FUNÇÃO: lifespan(app: FastAPI)
    Objetivo: Gerenciar eventos que ocorrem exata e unicamente quando o servidor LIGA ou DESLIGA.
    Uso: Injetado na inicialização do objeto FastAPI.
    ----------------------------------------------------------------------------------------------
    """
    print("Iniciando carregamento dos Modelos de Inteligência Artificial para a RAM...")
    inference_service.load_all_models()
    yield
    print("Desligando serviço, limpando memória...")

# Instância principal da aplicação FastAPI
app = FastAPI(
    title="HealthAI Diagnostics Backend",
    description="Backend Service and AI Engine for HealthAI. Protected by Exponential Rate Limit.",
    version="2.0.0",
    lifespan=lifespan
)

# Adiciona o middleware customizado de segurança ANTES do CORS
app.add_middleware(AdvancedExponentialRateLimiter, max_requests=30, window_seconds=60)

"""
----------------------------------------------------------------------------------------------
CONFIGURAÇÃO DE CORS Estrito
Objetivo: O Backend só aceita tráfego da própria infraestrutura (Firebase Hosting) e do localhost para dev.
Isso impede que scripts externos em outros domínios consumam nossa API.
----------------------------------------------------------------------------------------------
"""
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:4200", 
        "https://healthai-diagnostics.web.app", 
        "https://healthai-diagnostics.firebaseapp.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registra os roteadores modularizados (separação de responsabilidades / MVC)
app.include_router(anamnesis.router)
app.include_router(admin.router)

@app.get("/")
def read_root():
    """
    Rota de Health Check (Checagem de Saúde) para o Cloud Run.
    """
    return {"status": "HealthAI Backend (ML-Ready & Rate-Limited) is running"}
