"""
==================================================================================================
ARQUIVO: main.py (ENTRYPOINT DO BACKEND)
==================================================================================================
Objetivo:
Este é o ponto de entrada principal (Entrypoint) da aplicação backend, construída com o framework FastAPI.
Aqui defino o servidor HTTP, configuro a segurança (CORS), anexo as rotas (Controllers) e,
mais importante, gerencio o "Ciclo de Vida" (Lifespan) da aplicação, que é o momento onde os
modelos de Inteligência Artificial pesados são carregados na memória (RAM) antes do servidor começar a aceitar requisições.

Decisão Arquitetural:
Escolhi o FastAPI porque ele é assíncrono por padrão (ASGI), excelente para serviços que precisam
esperar chamadas de rede lentas (como as requisições para APIs de LLM externas, Gemini/OpenAI).
==================================================================================================
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.api.routers import anamnesis, admin
from app.services.inference import inference_service

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    ----------------------------------------------------------------------------------------------
    FUNÇÃO: lifespan(app: FastAPI)
    Objetivo: Gerenciar eventos que ocorrem exata e unicamente quando o servidor LIGA ou DESLIGA.
    Uso: Injetado na inicialização do objeto FastAPI.
    
    Detalhe Técnico (IA):
    Modelos de Machine Learning (como ResNet de Visão ou Random Forest Tabular) dependem de arquivos
    de pesos (weights/pickles/pth) que pesam gigabytes e demoram segundos ou minutos para serem lidos do HD.
    Se eu carregasse os modelos a cada requisição (dentro do endpoint HTTP), o tempo de resposta do
    paciente seria horrível.
    Portanto, faço o "Warm-up" (carregamento em cache na memória RAM) uma única vez durante
    este 'lifespan' (Cold Start).
    ----------------------------------------------------------------------------------------------
    """
    # Executado durante o STARTUP da aplicação (Cold Start)
    print("Iniciando carregamento dos Modelos de Inteligência Artificial para a RAM...")
    inference_service.load_all_models()
    yield
    # Executado durante o SHUTDOWN da aplicação (quando o servidor é morto, ex: CTRL+C)
    print("Desligando serviço, limpando memória...")

# Instância principal da aplicação FastAPI
app = FastAPI(
    title="HealthAI Diagnostics Backend",
    description="Backend Service and AI Engine for HealthAI.",
    version="2.0.0",
    lifespan=lifespan # Injetando a função de warm-up descrita acima
)

"""
----------------------------------------------------------------------------------------------
CONFIGURAÇÃO DE CORS (Cross-Origin Resource Sharing)
Objetivo: Segurança de Navegador.
Detalhe Técnico: Por padrão, navegadores bloqueiam requisições de um site (ex: localhost:4200 - Frontend Angular)
para um servidor rodando em outra porta (ex: localhost:8000 - Backend FastAPI). O CORS diz ao backend
quais sites são 'seguros' e permitidos para consumir a API.
----------------------------------------------------------------------------------------------
"""
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"], # Apenas o Angular é autorizado a bater nesta API localmente
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registra os roteadores modularizados (separação de responsabilidades / MVC)
# A rota 'anamnesis' cuida de diagnósticos de IA. A rota 'admin' cuida da troca de modelos ativos.
app.include_router(anamnesis.router)
app.include_router(admin.router)

@app.get("/")
def read_root():
    """
    ----------------------------------------------------------------------------------------------
    FUNÇÃO: read_root()
    Objetivo: Rota de "Health Check" (Checagem de Saúde).
    Uso: Usada por balanceadores de carga (Load Balancers como NGINX ou AWS ALB) para verificar
    se o serviço da API subiu e está respondendo com sucesso antes de rotear tráfego real para ele.
    ----------------------------------------------------------------------------------------------
    """
    return {"status": "HealthAI Backend (ML-Ready) is running"}
