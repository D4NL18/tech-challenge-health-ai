"""
==================================================================================================
ARQUIVO: routers/anamnesis.py (CONTROLLER DE API)
==================================================================================================
Objetivo:
Atuar como a interface entre o Frontend (Angular) e o "Cérebro" de IA (Inference Service).
Este arquivo é o que chamamos de 'Controller' no padrão MVC. Ele recebe a requisição HTTP POST,
desempacota a imagem e o JSON, valida os dados e envia para a camada de Machine Learning.

Conceito Técnico (Multipart/Form-Data):
Geralmente, APIs Rest usam 'application/json' para enviar dados. Mas JSON não suporta envio de 
arquivos binários (como Imagens de Raio-X). Por isso, uso `Form` (Multipart) para aceitar
ao mesmo tempo os dados em formato String (que converto de volta pra JSON) e o arquivo de Imagem.
==================================================================================================
"""

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from pydantic import ValidationError
import json

from app.models.schemas import DiagnosticResult, AnamnesisPayload
from app.services.inference import inference_service

# Instanciando o Router. Ele agrupa todas as rotas que começarem com '/api/v1/anamnesis'
router = APIRouter(
    prefix="/api/v1/anamnesis",
    tags=["Anamnesis"]
)

@router.post("/analyze", response_model=DiagnosticResult)
async def analyze_anamnesis(
    anamnesis_data: str = Form(..., description="String JSON contendo AnamnesisPayload"),
    image: UploadFile = File(None, description="Upload opcional de imagem médica")
):
    """
    ----------------------------------------------------------------------------------------------
    FUNÇÃO: analyze_anamnesis
    Objetivo: Endpoint ('/analyze') que dispara a análise da inteligência artificial.
    De Onde é Chamado: Pelo Frontend Angular, ao clicar no botão 'Realizar Triagem'.
    
    Detalhe Técnico (Validação Pydantic):
    1. O frontend envia `anamnesis_data` como uma String Pura.
    2. Uso `json.loads` para transformar a string em um Dicionário Python.
    3. Passo esse dicionário para a classe `AnamnesisPayload(**data_dict)`. O Pydantic
       valida instantaneamente se as idades, sintomas e doenças estão no formato correto.
       Se faltar um campo obrigatório, ele lança um `ValidationError`.
    ----------------------------------------------------------------------------------------------
    """
    try:
        # Conversão de String para JSON (Dicionário)
        data_dict = json.loads(anamnesis_data)
        # Validação estrita usando Pydantic
        payload = AnamnesisPayload(**data_dict)
    except json.JSONDecodeError:
        # Se a string não for um JSON válido, retorno erro 400 (Bad Request)
        raise HTTPException(status_code=400, detail="Formato JSON inválido no campo anamnesis_data")
    except ValidationError as e:
        # Se faltar campo obrigatório na classe AnamnesisPayload, retorno 422 (Unprocessable Entity)
        raise HTTPException(status_code=422, detail=f"Erro de validação Pydantic: {e.errors()}")

    # Tratamento da Imagem Binária
    image_bytes = None
    if image:
        # A palavra 'await' suspende a execução até que o disco/rede termine de ler a imagem,
        # liberando o FastAPI para atender outros pacientes simultaneamente (Assincronismo).
        image_bytes = await image.read()

    # Chama a camada de Serviço. É aqui que os dados saem do "Mundo Web" e entram no "Mundo da IA".
    result_dict = inference_service.analyze_full_anamnesis(
        payload=payload,
        image_bytes=image_bytes
    )

    # Retorna os resultados formatados no schema DiagnosticResult, garantindo que o Frontend
    # receba exatamente os campos que ele espera.
    return DiagnosticResult(**result_dict)
