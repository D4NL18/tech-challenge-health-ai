from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.api.routers import anamnesis
from app.services.inference import inference_service

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Executado durante o STARTUP da aplicação (Cold Start)
    print("Iniciando carregamento dos Modelos de Inteligência Artificial para a RAM...")
    inference_service.load_all_models()
    yield
    # Executado durante o SHUTDOWN da aplicação
    print("Desligando serviço, limpando memória...")

app = FastAPI(
    title="HealthAI Diagnostics Backend",
    description="Backend Service and AI Engine for HealthAI.",
    version="2.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registra os roteadores modularizados
app.include_router(anamnesis.router)

@app.get("/")
def read_root():
    return {"status": "HealthAI Backend (ML-Ready) is running"}
