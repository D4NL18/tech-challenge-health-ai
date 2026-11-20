"""
==================================================================================================
MÓDULO: app/core/settings.py — Configuração do Assistente Médico (Fase 3)
==================================================================================================
Objetivo:
    `AssistantSettings` é a ÚNICA fonte de configuração do assistente (ARCHITECTURE.md, seção 6):
    nenhum módulo do assistente lê `os.environ` diretamente. Os valores vêm de variáveis de
    ambiente (nome do campo em maiúsculas, ex.: `ASSISTANT_ENABLED`) ou do `.env` local.

Decisões:
    - Sem valor padrão inseguro para segredos: `doctor_password` e as URLs de banco (que carregam
      credencial) são `SecretStr` opcionais; sem segredo configurado, o recurso não sobe.
    - Parâmetros ainda não decididos (candidato padrão, modelo de embeddings, versão do corpus,
      limiar do RAG, SLA de exames) ficam `None` até a fase dona fixá-los (F3, F6, F8); nada de
      número mágico inventado aqui.
    - `doctor_username` vira `actor_id` na trilha de auditoria (RIPD 5.4, decisão PA-07): só é
      aceito no formato funcional `^[a-z][a-z0-9_-]{2,31}$`, sem sequência de 5+ dígitos e sem
      casar com nenhum padrão de `PII_PATTERNS`. Fora disso, a configuração é REJEITADA (não
      mascarada no log).
==================================================================================================
"""

from __future__ import annotations

import re
from functools import lru_cache
from typing import Final, Literal

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.core.pii_patterns import matches_any_pii

# Formato funcional do identificador de conta (RIPD 5.4).
USERNAME_PATTERN: Final[re.Pattern[str]] = re.compile(r"^[a-z][a-z0-9_-]{2,31}$")
# Sequência longa de dígitos sugere documento embutido no username (RIPD 5.4).
LONG_DIGIT_RUN_PATTERN: Final[re.Pattern[str]] = re.compile(r"\d{5,}")

# Modelo fixado no scorecard congelado (checkpoint F0, D13: `pinned_model_id`).
DEFAULT_GEMINI_FALLBACK_MODEL: Final[str] = "gemini-3.8-flash"

LlmAuthMode = Literal["none", "cloud_run_id_token"]


class AssistantSettings(BaseSettings):
    """Configuração tipada do assistente, lida de variáveis de ambiente e do `.env`."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
        # O erro de validação não ecoa o valor recebido (username rejeitado pode conter PII e as
        # URLs de banco contêm senha).
        hide_input_in_errors=True,
    )

    # Flag principal (ASSISTANT_ENABLED). Desligada: rotas do assistente respondem 501 e nenhum
    # recurso do assistente é inicializado.
    assistant_enabled: bool = False

    # Fine-tuned usado antes de existir escolha no painel (ADR-002 2.3); definido na F3.
    assistant_default_candidate: str | None = None
    # Onde fica a escolha do modelo ativo: objeto no Cloud Storage (prod) ou arquivo local (dev).
    active_model_store_uri: str | None = None

    # Endereço do servidor de LLM: `healthai-llm` (prod) ou `llama-swap` local (dev).
    llm_service_url: str | None = None
    # Autenticação no `healthai-llm`: ID token do Cloud Run em produção, nenhuma em dev.
    llm_auth_mode: LlmAuthMode = "none"
    # Modelo da contingência sem dados de paciente (P-048, P-051).
    gemini_fallback_model: str = DEFAULT_GEMINI_FALLBACK_MODEL

    # Pooler do Supabase em modo transação (app) e conexão direta (migrações/seed). Contêm senha.
    database_url: SecretStr | None = None
    database_direct_url: SecretStr | None = None

    # RAG (F6): modelo de embeddings da ablação, versão ativa do corpus e corte de relevância.
    embedding_model: str | None = None
    corpus_version: str | None = None
    rag_min_score: float | None = Field(default=None, ge=0.0, le=1.0)

    # Prazo, em dias, para alerta de exame pendente (P-045; valor fechado na F8, PA-06).
    exam_sla_days: int | None = Field(default=None, ge=1)

    # Usuário médico de demonstração (cenário A). O username vira `actor_id` na auditoria.
    doctor_username: str | None = None
    doctor_password: SecretStr | None = None

    @field_validator("doctor_username")
    @classmethod
    def validate_doctor_username(cls, username: str | None) -> str | None:
        """Aceita só identificador funcional, sem PII (RIPD 5.4 / PA-07). Não ecoa o valor no erro."""
        if username is None:
            return None
        if not USERNAME_PATTERN.fullmatch(username):
            raise ValueError("doctor_username fora do formato ^[a-z][a-z0-9_-]{2,31}$")
        if LONG_DIGIT_RUN_PATTERN.search(username):
            raise ValueError("doctor_username não pode conter sequência de 5 ou mais dígitos")
        if matches_any_pii(username):
            raise ValueError("doctor_username não pode conter dado pessoal (PII_PATTERNS)")
        return username


@lru_cache(maxsize=1)
def get_settings() -> AssistantSettings:
    """Instância única (em cache) das configurações. Testes usam `get_settings.cache_clear()`."""
    return AssistantSettings()
