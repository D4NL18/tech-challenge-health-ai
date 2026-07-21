from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from pydantic import ValidationError
import json

from app.models.schemas import DiagnosticResult, AnamnesisPayload
from app.services.inference import inference_service

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
    Recebe os dados do formulário e repassa para a camada de serviço/inferência.
    """
    try:
        data_dict = json.loads(anamnesis_data)
        payload = AnamnesisPayload(**data_dict)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Formato JSON inválido no campo anamnesis_data")
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=f"Erro de validação Pydantic: {e.errors()}")

    image_bytes = None
    if image:
        image_bytes = await image.read()

    # Chama a camada de serviço que orquestra os modelos ML
    result_dict = inference_service.analyze_full_anamnesis(
        payload=payload,
        image_bytes=image_bytes
    )

    return DiagnosticResult(**result_dict)
