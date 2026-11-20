"""
Smoke das fixtures compartilhadas do ``tests/conftest.py`` (F0, passo 0.5).

Garante que a infraestrutura de teste usada da F1 à F11 funciona antes de qualquer fase depender dela.
O teste de Postgres pula sozinho (``pytest.skip``) quando o banco local não está acessível.
"""

from __future__ import annotations

import pytest
from sqlalchemy import text


def test_sqlite_session_runs_queries_in_memory(sqlite_session):
    sqlite_session.execute(text("CREATE TABLE sample (id INTEGER PRIMARY KEY, label TEXT)"))
    sqlite_session.execute(text("INSERT INTO sample (label) VALUES ('sintetico')"))
    assert sqlite_session.execute(text("SELECT COUNT(*) FROM sample")).scalar_one() == 1


def test_sqlite_session_is_isolated_between_tests(sqlite_session):
    tables = sqlite_session.execute(text("SELECT name FROM sqlite_master WHERE type='table'")).all()
    assert tables == []


def test_fake_chat_model_returns_scripted_responses_in_order(fake_chat_model):
    llm = fake_chat_model(["primeira", "segunda"])
    assert llm.invoke("pergunta 1").content == "primeira"
    assert llm.invoke("pergunta 2").content == "segunda"


def test_fake_chat_model_has_default_script(fake_chat_model):
    assert fake_chat_model().invoke("pergunta").content


def test_postgres_session_has_pgvector(postgres_session):
    extension = postgres_session.execute(
        text("SELECT extname FROM pg_extension WHERE extname = 'vector'")
    ).scalar_one_or_none()
    assert extension == "vector"


def test_postgres_session_fixture_marks_test_as_integration(request):
    # Este teste não usa o banco; confere que o hook marca apenas quem usa postgres_session.
    assert request.node.get_closest_marker("integration") is None


@pytest.mark.integration
def test_integration_marker_is_registered(request):
    assert request.node.get_closest_marker("integration") is not None
