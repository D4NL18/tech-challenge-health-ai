"""
Fixtures compartilhadas da suíte do backend (Fase 3 / F0, passo 0.5).

Objetivo:
    Dar a todas as fases (F1…F11) a mesma infraestrutura de teste, sem que nenhum teste
    dependa de serviço externo para rodar no job padrão do CI.

Fixtures:
    - ``sqlite_session``: sessão SQLAlchemy em SQLite em memória (lógica pura, rápida).
    - ``postgres_engine`` / ``postgres_session``: Postgres local com pgvector, lido de
      ``TEST_DATABASE_URL``. Pula com ``pytest.skip`` se o banco não estiver acessível.
      Todo teste que usa ``postgres_session`` recebe o marker ``integration`` na coleta.
    - ``fake_chat_model``: fábrica de ``FakeListChatModel`` com respostas roteirizadas
      (nenhuma chamada a LLM real; para chamadas reais existe o marker ``llm_live``).
    - ``settings_override``: sobrescreve ``AssistantSettings`` via variáveis de ambiente
      e limpa o cache de ``get_settings()`` antes e depois do teste.

Decisões:
    - Os imports de ``app.*``, SQLAlchemy e LangChain são tardios (dentro das fixtures), para
      que este conftest nunca quebre a coleta dos 27 testes antigos.
    - ``TEST_DATABASE_URL`` é uma variável própria de teste, e não ``DATABASE_URL``, para que
      um ``.env`` apontando para o Supabase nunca seja usado por engano. Por segurança,
      só hosts locais são aceitos, salvo ``ALLOW_REMOTE_TEST_DB=1``.
"""

from __future__ import annotations

import os
from collections.abc import Callable, Iterator
from urllib.parse import urlparse

import pytest

# URL padrão do Postgres local do docker-compose.dev.yml (credenciais só de desenvolvimento).
DEFAULT_TEST_DATABASE_URL = "postgresql+psycopg://healthai:healthai_dev@localhost:5433/healthai_dev"
LOCAL_DATABASE_HOSTS = {"localhost", "127.0.0.1", "::1", "postgres"}
POSTGRES_CONNECT_TIMEOUT_SECONDS = 3

# Respostas padrão do modelo falso: curtas, sem dado pessoal, só para exercitar o fluxo.
DEFAULT_FAKE_RESPONSES = [
    "Resposta roteirizada 1 (modelo falso).",
    "Resposta roteirizada 2 (modelo falso).",
]


# --------------------------------------------------------------------------------------------
# Hooks de coleta
# --------------------------------------------------------------------------------------------
def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    """Marca como ``integration`` todo teste que dependa do Postgres real.

    O marker precisa existir já na coleta para que ``-m "not integration"`` funcione;
    adicioná-lo dentro da fixture seria tarde demais para a seleção.
    """
    integration_marker = pytest.mark.integration
    for item in items:
        if "postgres_session" in getattr(item, "fixturenames", ()):
            item.add_marker(integration_marker)


# --------------------------------------------------------------------------------------------
# Determinismo
# --------------------------------------------------------------------------------------------
# Semente fixa, opt-in: os algoritmos genéticos (app/genetic) usam `random` e `numpy.random` sem
# semente, e o teste antigo `test_vrp_balanced_priority_distribution` falhava em ~10% das execuções.
# Com o job `test` bloqueando o deploy, teste intermitente é inaceitável. A fixture NÃO é autouse
# (achado I-1 da revisão F0): só os testes que a pedem via `usefixtures` ficam determinísticos,
# para não mascarar aleatoriedade em testes futuros. A causa real fica como dívida técnica:
# o GA do VRP não garante o balanceamento CRITICAL/HIGH (T4: `VRPSolver` com `seed` injetável e
# balanceamento como restrição ou passo de reparo).
TEST_RANDOM_SEED = 1234


@pytest.fixture
def deterministic_random_seed() -> None:
    """Fixa as sementes de ``random`` e ``numpy.random`` antes do teste que pedir a fixture."""
    import random

    random.seed(TEST_RANDOM_SEED)
    try:
        import numpy as np
    except ImportError:  # pragma: no cover - numpy é dependência do backend
        return
    np.random.seed(TEST_RANDOM_SEED)


# --------------------------------------------------------------------------------------------
# Banco de dados
# --------------------------------------------------------------------------------------------
@pytest.fixture
def sqlite_session() -> Iterator["Session"]:  # noqa: F821 (tipo importado tardiamente)
    """Sessão SQLAlchemy em SQLite em memória, isolada por teste.

    ``StaticPool`` mantém a mesma conexão, senão cada checkout veria um banco vazio.
    O teste cria as próprias tabelas (``Base.metadata.create_all(session.get_bind())``).
    """
    from sqlalchemy import create_engine
    from sqlalchemy.orm import Session
    from sqlalchemy.pool import StaticPool

    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    session = Session(bind=engine)
    try:
        yield session
    finally:
        session.rollback()
        session.close()
        engine.dispose()


def _resolve_test_database_url() -> str:
    """Lê a URL do banco de teste e recusa hosts remotos (proteção contra o Supabase)."""
    url = os.environ.get("TEST_DATABASE_URL", DEFAULT_TEST_DATABASE_URL)
    host = urlparse(url.replace("+psycopg", "")).hostname or ""
    is_remote_allowed = os.environ.get("ALLOW_REMOTE_TEST_DB") == "1"
    if host not in LOCAL_DATABASE_HOSTS and not is_remote_allowed:
        pytest.skip(f"TEST_DATABASE_URL aponta para host não local ({host}); defina ALLOW_REMOTE_TEST_DB=1")
    return url


@pytest.fixture(scope="session")
def postgres_engine() -> Iterator["Engine"]:  # noqa: F821
    """Engine do Postgres de teste com a extensão ``vector`` habilitada; pula se inacessível."""
    try:
        from sqlalchemy import create_engine, text
        from sqlalchemy.exc import SQLAlchemyError
    except ImportError as exc:  # pragma: no cover - dependência ausente no ambiente
        pytest.skip(f"SQLAlchemy indisponível: {exc}")

    url = _resolve_test_database_url()
    engine = create_engine(
        url,
        connect_args={"connect_timeout": POSTGRES_CONNECT_TIMEOUT_SECONDS},
        pool_pre_ping=True,
    )
    try:
        with engine.begin() as connection:
            connection.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
    except SQLAlchemyError as exc:
        engine.dispose()
        # Só o tipo do erro: a mensagem pode conter a URL com senha.
        pytest.skip(f"Postgres de teste inacessível ({type(exc).__name__}); suba o docker-compose.dev.yml")
    yield engine
    engine.dispose()


@pytest.fixture
def postgres_session(postgres_engine) -> Iterator["Session"]:  # noqa: F821
    """Sessão no Postgres de teste dentro de uma transação desfeita ao fim do teste.

    ``join_transaction_mode="create_savepoint"`` permite ``session.commit()`` no código
    testado sem persistir nada: o rollback externo apaga tudo.
    """
    from sqlalchemy.orm import Session

    connection = postgres_engine.connect()
    outer_transaction = connection.begin()
    session = Session(bind=connection, join_transaction_mode="create_savepoint")
    try:
        yield session
    finally:
        session.close()
        outer_transaction.rollback()
        connection.close()


# --------------------------------------------------------------------------------------------
# LLM falso
# --------------------------------------------------------------------------------------------
@pytest.fixture
def fake_chat_model() -> Callable[..., "FakeListChatModel"]:  # noqa: F821
    """Fábrica de ``FakeListChatModel`` com respostas roteirizadas, na ordem dada.

    Uso::

        def test_x(fake_chat_model):
            llm = fake_chat_model(["primeira", "segunda"])
            assert llm.invoke("pergunta").content == "primeira"

    Sem argumento, usa ``DEFAULT_FAKE_RESPONSES``. Quando a lista acaba, o modelo recomeça.
    """
    from langchain_core.language_models.fake_chat_models import FakeListChatModel

    def _build(responses: list[str] | None = None) -> FakeListChatModel:
        scripted = list(responses) if responses is not None else list(DEFAULT_FAKE_RESPONSES)
        return FakeListChatModel(responses=scripted)

    return _build


# --------------------------------------------------------------------------------------------
# Settings
# --------------------------------------------------------------------------------------------
def _to_env_value(value: object) -> str:
    """Converte um valor Python para o texto que o pydantic-settings lê do ambiente."""
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


@pytest.fixture
def settings_override(monkeypatch: pytest.MonkeyPatch) -> Iterator[Callable[..., "AssistantSettings"]]:  # noqa: F821
    """Sobrescreve campos de ``AssistantSettings`` e devolve a instância de ``get_settings()``.

    Funciona por variável de ambiente (nome do campo em maiúsculas), então vale também para
    módulos que importaram ``get_settings`` antes do teste. ``None`` remove a variável.
    O cache é limpo na entrada e na saída; o ``monkeypatch`` restaura o ambiente depois.

    Uso::

        def test_x(settings_override):
            settings = settings_override(assistant_enabled=False, exam_sla_days=30)
    """
    from app.core import settings as settings_module

    settings_module.get_settings.cache_clear()

    def _apply(**overrides: object) -> "AssistantSettings":  # noqa: F821
        for field_name, value in overrides.items():
            env_name = field_name.upper()
            if value is None:
                monkeypatch.delenv(env_name, raising=False)
                continue
            monkeypatch.setenv(env_name, _to_env_value(value))
        settings_module.get_settings.cache_clear()
        return settings_module.get_settings()

    yield _apply
    settings_module.get_settings.cache_clear()
