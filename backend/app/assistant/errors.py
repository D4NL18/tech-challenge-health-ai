"""
==================================================================================================
MÓDULO: app/assistant/errors.py — Erros de domínio do Assistente Médico
==================================================================================================
Objetivo:
    Toda exceção de domínio do assistente herda de `AssistantDomainError(code, http_status,
    public_message)`. O código interno segue o formato obrigatório `AST-NNN` (regra global de
    tratamento de erros) e pertence a uma faixa reservada por fase, para que fases paralelas não
    colidam (ARCHITECTURE.md, seção 4.4):

        AST-001…019    F5     guardrails e auditoria
        AST-020…049    F7/F8  LLM e fluxos (ex.: AST-022 modelo carregando, 503 + Retry-After)
        AST-050…069    F9     API, auth e seleção de modelo (AST-050: assistente desativado,
                              usado desde a F0 pelo stub 501 do bootstrap)
        AST-4xx        F4     prontuário (ex.: AST-404 paciente não encontrado)

    O handler traduz a exceção num JSON `{"error", "code"}` SEM stack trace e sem detalhes
    internos. Na F5 o handler global (`app/core/exception_handlers.py`) acrescenta o `trace_id`.
==================================================================================================
"""

from __future__ import annotations

import logging
import re
from typing import Final

from fastapi import Request
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)

ERROR_CODE_FORMAT: Final[re.Pattern[str]] = re.compile(r"^AST-(\d{3})$")
MIN_HTTP_ERROR_STATUS: Final[int] = 400
MAX_HTTP_ERROR_STATUS: Final[int] = 599

# Faixas reservadas por fase (números sem o prefixo `AST-`; ARCHITECTURE.md 4.4).
AST_CODE_RANGES: Final[dict[str, range]] = {
    "F4": range(400, 500),
    "F5": range(1, 20),
    "F7_F8": range(20, 50),
    "F9": range(50, 70),
}

# Códigos já definidos pela arquitetura (as fases donas criam as subclasses).
ASSISTANT_DISABLED_CODE: Final[str] = "AST-050"
FLOW_NOT_FOUND_CODE: Final[str] = "AST-020"
FINE_TUNED_UNAVAILABLE_CODE: Final[str] = "AST-021"
MODEL_LOADING_CODE: Final[str] = "AST-022"
CANDIDATE_INELIGIBLE_CODE: Final[str] = "AST-051"
CANDIDATE_UNAVAILABLE_CODE: Final[str] = "AST-052"
PATIENT_NOT_FOUND_CODE: Final[str] = "AST-404"

HTTP_NOT_IMPLEMENTED: Final[int] = 501


def is_reserved_code(code: str) -> bool:
    """True se `code` tem o formato `AST-NNN` e cai numa das faixas reservadas."""
    match = ERROR_CODE_FORMAT.fullmatch(code)
    if not match:
        return False
    number = int(match.group(1))
    return any(number in numbers for numbers in AST_CODE_RANGES.values())


class AssistantDomainError(Exception):
    """
    Base de todas as exceções de domínio do assistente.

    - `code`: código interno `AST-NNN` dentro de uma faixa reservada (o frontend decide por ele,
      nunca pela mensagem);
    - `http_status`: status HTTP de erro (4xx/5xx), nunca um "falso 200";
    - `public_message`: texto seguro para o usuário final; nunca leva dado de paciente, segredo
      ou detalhe interno.
    """

    def __init__(self, code: str, http_status: int, public_message: str) -> None:
        if not is_reserved_code(code):
            raise ValueError(f"Código de erro fora do formato AST-NNN ou de faixa reservada: {code!r}")
        if not MIN_HTTP_ERROR_STATUS <= http_status <= MAX_HTTP_ERROR_STATUS:
            raise ValueError(f"http_status de erro inválido: {http_status}")
        super().__init__(public_message)
        self.code = code
        self.http_status = http_status
        self.public_message = public_message

    def to_payload(self) -> dict[str, str]:
        """Corpo público da resposta de erro: só mensagem amigável e código interno."""
        return {"error": self.public_message, "code": self.code}


class AssistantDisabledError(AssistantDomainError):
    """Rota do assistente chamada com `assistant_enabled=False` ou ainda não implementada (F0)."""

    PUBLIC_MESSAGE: Final[str] = "O assistente médico não está disponível neste ambiente."

    def __init__(self) -> None:
        super().__init__(ASSISTANT_DISABLED_CODE, HTTP_NOT_IMPLEMENTED, self.PUBLIC_MESSAGE)


async def assistant_domain_error_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Traduz `AssistantDomainError` no envelope de erro padronizado, sem stack trace.
    Loga só código, status e rota (nunca o corpo da requisição nem o objeto da exceção).
    """
    if not isinstance(exc, AssistantDomainError):
        raise exc
    logger.warning(
        "assistant_domain_error code=%s status=%s path=%s",
        exc.code,
        exc.http_status,
        request.url.path,
    )
    return JSONResponse(status_code=exc.http_status, content=exc.to_payload())
