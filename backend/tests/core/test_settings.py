"""
Testes TDD de ``app.core.settings`` (F0, passo 0.1).

Contrato (plano F0 0.1, ARCHITECTURE.md seção 6 e decisões do checkpoint F0):
    - ``AssistantSettings(BaseSettings)`` lê variáveis de ambiente sem prefixo (nome do campo
      em maiúsculas, ex.: ``ASSISTANT_ENABLED``) e aceita ``_env_file=None`` para isolar testes.
    - Todos os campos têm default, então ``AssistantSettings(_env_file=None)`` funciona sem ambiente.
    - ``assistant_enabled`` é ``False`` por padrão.
    - ``llm_auth_mode`` aceita só ``"none"`` | ``"cloud_run_id_token"`` (default ``"none"``).
    - ``gemini_fallback_model == "gemini-3.8-flash"`` (D13, ``pinned_model_id`` do scorecard).
    - ``exam_sla_days`` é ``int`` e ``rag_min_score`` é ``float``.
    - ``doctor_password`` não tem default inseguro (``None``) e não aparece em ``repr``/``str``.
    - ``doctor_username`` (PA-07): casa ``^[a-z][a-z0-9_-]{2,31}$`` e não casa nenhum
      padrão de ``PII_PATTERNS``; caso contrário, ``ValidationError``.
    - ``get_settings()`` devolve a mesma instância (cache com ``cache_clear()``).
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.core.settings import AssistantSettings, get_settings

SETTINGS_FIELDS = [
    "assistant_enabled",
    "assistant_default_candidate",
    "active_model_store_uri",
    "llm_service_url",
    "llm_auth_mode",
    "gemini_fallback_model",
    "database_url",
    "database_direct_url",
    "embedding_model",
    "corpus_version",
    "rag_min_score",
    "exam_sla_days",
    "doctor_username",
    "doctor_password",
]

# Valor sintético usado só para verificar que o segredo não vaza na representação.
SYNTHETIC_PASSWORD = "senha-sintetica-de-teste-123"


@pytest.fixture
def clean_env(monkeypatch: pytest.MonkeyPatch):
    """Remove do ambiente toda variável que alimenta ``AssistantSettings`` e limpa o cache."""
    for field_name in SETTINGS_FIELDS:
        monkeypatch.delenv(field_name.upper(), raising=False)
    get_settings.cache_clear()
    yield monkeypatch
    get_settings.cache_clear()


def _isolated_settings(**overrides: object) -> AssistantSettings:
    """Instância sem ler o ``.env`` do disco."""
    return AssistantSettings(_env_file=None, **overrides)


class TestDefaults:
    def test_declares_every_planned_field(self, clean_env):
        declared = set(AssistantSettings.model_fields)
        missing = [name for name in SETTINGS_FIELDS if name not in declared]
        assert missing == []

    def test_builds_without_any_environment(self, clean_env):
        assert isinstance(_isolated_settings(), AssistantSettings)

    def test_assistant_is_disabled_by_default(self, clean_env):
        assert _isolated_settings().assistant_enabled is False

    def test_llm_auth_mode_defaults_to_none(self, clean_env):
        assert _isolated_settings().llm_auth_mode == "none"

    def test_gemini_fallback_model_is_pinned(self, clean_env):
        assert _isolated_settings().gemini_fallback_model == "gemini-3.8-flash"

    def test_doctor_password_has_no_insecure_default(self, clean_env):
        assert _isolated_settings().doctor_password is None


class TestLlmAuthMode:
    @pytest.mark.parametrize("mode", ["none", "cloud_run_id_token"])
    def test_accepts_allowed_modes(self, clean_env, mode):
        assert _isolated_settings(llm_auth_mode=mode).llm_auth_mode == mode

    @pytest.mark.parametrize("mode", ["api_key", "NONE", "", "oauth"])
    def test_rejects_other_modes(self, clean_env, mode):
        with pytest.raises(ValidationError):
            _isolated_settings(llm_auth_mode=mode)


class TestEnvironmentReading:
    def test_reads_assistant_enabled_from_env(self, clean_env):
        clean_env.setenv("ASSISTANT_ENABLED", "true")
        assert _isolated_settings().assistant_enabled is True

    def test_reads_and_coerces_numeric_fields(self, clean_env):
        clean_env.setenv("EXAM_SLA_DAYS", "45")
        clean_env.setenv("RAG_MIN_SCORE", "0.35")
        settings = _isolated_settings()
        assert settings.exam_sla_days == 45
        assert isinstance(settings.exam_sla_days, int)
        assert settings.rag_min_score == pytest.approx(0.35)

    def test_reads_llm_auth_mode_from_env(self, clean_env):
        clean_env.setenv("LLM_AUTH_MODE", "cloud_run_id_token")
        assert _isolated_settings().llm_auth_mode == "cloud_run_id_token"

    def test_invalid_llm_auth_mode_in_env_fails(self, clean_env):
        clean_env.setenv("LLM_AUTH_MODE", "api_key")
        with pytest.raises(ValidationError):
            _isolated_settings()

    def test_reads_string_fields_from_env(self, clean_env):
        clean_env.setenv("LLM_SERVICE_URL", "http://localhost:8080")
        clean_env.setenv("CORPUS_VERSION", "v-teste")
        settings = _isolated_settings()
        assert settings.llm_service_url == "http://localhost:8080"
        assert settings.corpus_version == "v-teste"


class TestGetSettingsCache:
    def test_returns_assistant_settings(self, clean_env):
        assert isinstance(get_settings(), AssistantSettings)

    def test_returns_the_same_cached_instance(self, clean_env):
        assert get_settings() is get_settings()

    def test_cache_clear_rereads_environment(self, clean_env):
        clean_env.setenv("ASSISTANT_ENABLED", "false")
        first = get_settings()
        clean_env.setenv("ASSISTANT_ENABLED", "true")
        assert get_settings() is first  # cache ainda vale
        get_settings.cache_clear()
        second = get_settings()
        assert second is not first
        assert second.assistant_enabled is True

    def test_settings_override_fixture_applies_and_clears_cache(self, settings_override):
        settings = settings_override(assistant_enabled=True, exam_sla_days=30)
        assert settings.assistant_enabled is True
        assert settings.exam_sla_days == 30
        assert get_settings() is settings


class TestDoctorCredentials:
    @pytest.mark.parametrize("username", ["medico_demo", "dr-ana", "abc", "m" + "a" * 31, "medico01"])
    def test_accepts_valid_usernames(self, clean_env, username):
        assert _isolated_settings(doctor_username=username).doctor_username == username

    @pytest.mark.parametrize(
        "username",
        [
            "Medico",  # maiúscula
            "ab",  # curto demais (mínimo 3)
            "m" + "a" * 32,  # longo demais (máximo 32)
            "1medico",  # começa com dígito
            "medico.demo",  # ponto não permitido
            "médico",  # acento não permitido
            "medico demo",  # espaço
        ],
    )
    def test_rejects_usernames_outside_regex(self, clean_env, username):
        with pytest.raises(ValidationError):
            _isolated_settings(doctor_username=username)

    @pytest.mark.parametrize(
        "username",
        [
            "a12345678909",  # contém um CPF (PA-07: identificador funcional, nunca documento)
            "a11988887777",  # contém um telefone com DDD
            "crm123456",  # contém um registro de CRM
        ],
    )
    def test_rejects_usernames_that_match_pii_patterns(self, clean_env, username):
        with pytest.raises(ValidationError):
            _isolated_settings(doctor_username=username)

    def test_reads_doctor_username_from_env(self, clean_env):
        clean_env.setenv("DOCTOR_USERNAME", "medico_demo")
        assert _isolated_settings().doctor_username == "medico_demo"

    def test_doctor_password_does_not_leak_in_representation(self, clean_env):
        settings = _isolated_settings(doctor_password=SYNTHETIC_PASSWORD)
        assert SYNTHETIC_PASSWORD not in repr(settings)
        assert SYNTHETIC_PASSWORD not in str(settings)
