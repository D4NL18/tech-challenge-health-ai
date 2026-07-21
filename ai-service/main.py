from fastapi import FastAPI, UploadFile, File, Form
from pydantic import BaseModel
from typing import Optional

app = FastAPI(
    title="HealthAI Diagnostics - AI Service",
    description="Microservice for NLP and Computer Vision inference.",
    version="1.0.0"
)

class InferenceResult(BaseModel):
    risk_level: str
    confidence: float
    description: str

@app.get("/")
def read_root():
    return {"status": "AI Service is running"}

@app.post("/api/v1/analyze/text", response_model=InferenceResult)
def analyze_text(symptoms: str = Form(...)):
    # Mock behavior for NLP
    return {
        "risk_level": "Moderate",
        "confidence": 0.85,
        "description": f"Sintomas analisados sugerem necessidade de avaliação médica presencial."
    }

@app.post("/api/v1/analyze/image", response_model=InferenceResult)
async def analyze_image(file: UploadFile = File(...)):
    # Mock behavior for Vision
    return {
        "risk_level": "High",
        "confidence": 0.92,
        "description": f"Imagem {file.filename} processada. Padrão anômalo detectado."
    }
