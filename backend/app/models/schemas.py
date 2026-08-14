"""
==================================================================================================
ARQUIVO: models/schemas.py (MODELOS DE DADOS / DTOs)
==================================================================================================
Objetivo:
Definir estritamente as 'Formas' (Schemas/Interfaces) dos dados que entram e saem da API.
Este arquivo utiliza a biblioteca 'Pydantic'. O Python é uma linguagem de tipagem dinâmica, o que
poderia ser perigoso em APIs (ex: esperar um número e receber uma string). O Pydantic força o Python
a agir com Tipagem Estática (como TypeScript ou Java) nas bordas da aplicação.
==================================================================================================
"""

from pydantic import BaseModel, Field
from typing import Optional

class DiagnosticResult(BaseModel):
    """
    ----------------------------------------------------------------------------------------------
    CLASSE: DiagnosticResult
    Objetivo: O DTO (Data Transfer Object) de Saída.
    Sempre que a IA terminar o cálculo, este será o molde exato que enviarei de volta para o
    Frontend Angular. Garantir essa estrutura previne que a tela do paciente quebre por falta de campos.
    ----------------------------------------------------------------------------------------------
    """
    risk_level: str = Field(..., description="Nível de risco calculado pela IA (ex: Baixo, Moderado, Alto)")
    confidence: float = Field(..., description="Grau de confiança/probabilidade da IA na predição (0.0 a 1.0)")
    description: str = Field(..., description="Descrição legível ou laudo simplificado do diagnóstico")
    model_used: Optional[str] = Field(None, description="Nome do algoritmo principal que gerou este laudo")

class AnamnesisPayload(BaseModel):
    """
    ----------------------------------------------------------------------------------------------
    CLASSE: AnamnesisPayload
    Objetivo: O DTO (Data Transfer Object) de Entrada.
    Quando o médico ou paciente clica em "Realizar Triagem", este é o contrato obrigatório que o JSON
    deve seguir. Se o frontend enviar algo diferente, a API devolve um erro 422 automaticamente sem
    nem chegar no modelo de IA.
    ----------------------------------------------------------------------------------------------
    """
    patient_id: Optional[str] = None
    age: int = Field(..., description="Idade da paciente") # "..." significa que o campo é Obrigatório
    symptoms: str = Field(..., description="Sintomas em forma de string pré-formatada")
    disease: str = Field(..., description="Doença alvo selecionada no frontend ('pcos' ou 'cancer')")
    medical_history: Optional[str] = Field(None, description="Histórico prévio")
    tabular_data: Optional[dict] = Field(None, description="Dicionário com as métricas quantitativas (ex: tamanho, raio)")
    open_text: Optional[str] = Field(None, description="Relato livre escrito pelo usuário para a LLM")
