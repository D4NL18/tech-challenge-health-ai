from pydantic import BaseModel, Field
from typing import Optional

class DiagnosticResult(BaseModel):
    risk_level: str = Field(..., description="Nível de risco calculado pela IA (ex: Low, Moderate, High)")
    confidence: float = Field(..., description="Grau de confiança da IA na predição (0.0 a 1.0)")
    description: str = Field(..., description="Descrição legível ou laudo simplificado do diagnóstico")
    model_used: Optional[str] = Field(None, description="Nome do algoritmo que gerou este laudo")

class AnamnesisPayload(BaseModel):
    patient_id: Optional[str] = None
    age: int = Field(..., description="Idade da paciente")
    symptoms: str = Field(..., description="Texto livre descrevendo os sintomas da paciente")
    medical_history: Optional[str] = Field(None, description="Informações médicas prévias ou dados tabulares formatados")
