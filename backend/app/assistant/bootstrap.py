"""
==================================================================================================
MÓDULO: app/assistant/bootstrap.py — Ponto único de ligação do assistente no backend
==================================================================================================
Objetivo:
    Expor as DUAS únicas funções que o `app/main.py` conhece (ARCHITECTURE.md, seção 5):

      - `register_assistant(app)`: chamada na importação do `main.py`, depois dos `include_router`
        legados. Registra routers e handlers do assistente conforme as flags. Na F0: router stub
        `/api/v1/assistant/*` que responde 501 (`AST-050`).
      - `init_assistant_resources()`: PRIMEIRA instrução do `lifespan`, antes de
        `inference_service.load_all_models()`. Na F0 não inicializa nada.

    Dali em diante cada fase liga o que produz AQUI, sem tocar no `main.py`.

Regras (ARCHITECTURE.md 5.3 e decisão A1 do checkpoint F0):
    1. Falha isolada: erro do assistente nunca derruba o backend; as Fases 1 e 2 continuam no ar.
    2. Sem trabalho pesado nem bloqueio no startup: a inicialização (e, na F7, o aquecimento do
       LLM, P-052) roda numa thread própria e daemon, disparada e NÃO esperada. Assim nunca
       bloqueia o event loop nem atrasa a carga dos modelos legados.
    3. Idempotência: chamar as funções mais de uma vez não duplica routers nem recursos.
==================================================================================================
"""

from __future__ import annotations

import logging
import threading
from collections.abc import Callable
from typing import Final

from fastapi import APIRouter, FastAPI
from pydantic import ValidationError

from app.assistant.errors import (
    AssistantDisabledError,
    AssistantDomainError,
    assistant_domain_error_handler,
)
from app.core.settings import AssistantSettings, get_settings

logger = logging.getLogger(__name__)

ASSISTANT_API_PREFIX: Final[str] = "/api/v1/assistant"
STUB_HTTP_METHODS: Final[list[str]] = ["GET", "POST", "PUT", "PATCH", "DELETE"]
INIT_THREAD_NAME: Final[str] = "assistant-init"
# Marcador em `app.state` que torna `register_assistant` idempotente por instância de app.
REGISTERED_STATE_FLAG: Final[str] = "assistant_registered"

# Passos de inicialização em segundo plano, em ordem. Vazio na F0; cada fase acrescenta o seu
# (F4 `init_records_db`, F6 `init_retriever`, F7 `init_assistant_service` + aquecimento...).
InitStep = Callable[[AssistantSettings], None]
_INIT_STEPS: Final[list[InitStep]] = []

_init_lock = threading.Lock()
_init_thread: threading.Thread | None = None


def _load_settings_safely() -> AssistantSettings | None:
    """
    Lê as configurações sem derrubar o backend. Configuração inválida (ex.: `doctor_username`
    fora do formato do RIPD 5.4) desativa o assistente; o log traz só os campos com erro,
    nunca os valores informados.
    """
    try:
        return get_settings()
    except ValidationError as error:
        invalid_fields = [".".join(str(part) for part in item["loc"]) for item in error.errors()]
        logger.error("assistant_settings_invalid fields=%s; assistente desativado", invalid_fields)
        return None


def _is_assistant_enabled() -> bool:
    settings = _load_settings_safely()
    return settings is not None and settings.assistant_enabled


def _build_stub_router() -> APIRouter:
    """Router F0: qualquer rota `/api/v1/assistant/*` responde 501 `AST-050` (sai na F9)."""
    router = APIRouter(prefix=ASSISTANT_API_PREFIX, tags=["Assistente Médico"])

    @router.api_route("", methods=STUB_HTTP_METHODS, include_in_schema=False)
    @router.api_route("/{path:path}", methods=STUB_HTTP_METHODS, include_in_schema=False)
    async def assistant_not_available(path: str = "") -> None:
        raise AssistantDisabledError()

    return router


def register_assistant(app: FastAPI) -> None:
    """
    Liga o assistente ao app conforme as flags. F0: handler de erro de domínio + router stub 501
    (com a flag desligada; enquanto não há rota real, também com a flag ligada).
    Idempotente: a segunda chamada no mesmo app não registra nada.
    """
    if getattr(app.state, REGISTERED_STATE_FLAG, False):
        return
    app.add_exception_handler(AssistantDomainError, assistant_domain_error_handler)
    app.include_router(_build_stub_router())
    setattr(app.state, REGISTERED_STATE_FLAG, True)
    logger.info("assistant_registered enabled=%s mode=stub", _is_assistant_enabled())


def _run_init_steps(settings: AssistantSettings) -> None:
    """Executa os passos em sequência; falha de um passo é logada e não derruba o processo."""
    for step in _INIT_STEPS:
        try:
            step(settings)
        except Exception as error:  # noqa: BLE001 - falha isolada exigida pela ARCHITECTURE 5.3
            logger.error(
                "assistant_init_step_failed step=%s error_type=%s",
                getattr(step, "__name__", "unknown"),
                type(error).__name__,
            )


def init_assistant_resources() -> None:
    """
    Dispara a inicialização dos recursos do assistente numa thread daemon e retorna na hora.
    Flag desligada (ou configuração inválida): não faz nada. Idempotente: não cria uma segunda
    thread enquanto a primeira existir. F0: a lista de passos está vazia (no-op).
    """
    global _init_thread
    settings = _load_settings_safely()
    if settings is None or not settings.assistant_enabled:
        return
    with _init_lock:
        if _init_thread is not None:
            return
        _init_thread = threading.Thread(
            target=_run_init_steps, args=(settings,), name=INIT_THREAD_NAME, daemon=True
        )
        _init_thread.start()
