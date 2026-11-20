"""
Testes TDD de ``app.assistant.bootstrap`` e do ponto de ligação no ``app/main.py`` (F0, passo 0.4).

Contrato (plano F0 0.4, ARCHITECTURE.md seção 5 e decisões do checkpoint F0):
    - ``register_assistant(app)`` registra o router stub ``/api/v1/assistant/*``; com
      ``assistant_enabled=False`` toda rota responde 501 no envelope de erro padronizado
      ``{"error": <mensagem pública>, "code": "AST-NNN"}``, sem stacktrace.
    - ``register_assistant`` é idempotente: chamar duas vezes não duplica rotas.
    - ``init_assistant_resources()`` é síncrona, não lança e não bloqueia (o aquecimento,
      a partir da F7, roda em thread própria); na F0 é praticamente um no-op.
    - Em ``backend/app/main.py``: ``init_assistant_resources()`` é a PRIMEIRA instrução do
      ``lifespan`` (antes de ``inference_service.load_all_models()``) e ``register_assistant(app)``
      vem depois de todos os ``app.include_router``.

Para não carregar os modelos pesados do ``lifespan`` real, os testes HTTP montam um
``FastAPI()`` mínimo; o ``main.py`` é verificado por inspeção do código-fonte (AST).
"""

from __future__ import annotations

import ast
import inspect
import re
import time
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.assistant.bootstrap import init_assistant_resources, register_assistant
from app.assistant.errors import is_reserved_code

ASSISTANT_PREFIX = "/api/v1/assistant"
ASK_PATH = f"{ASSISTANT_PREFIX}/ask"
MAIN_PY = Path(__file__).resolve().parents[2] / "app" / "main.py"
INIT_MAX_SECONDS = 0.5
STACKTRACE_MARKERS = ("Traceback", 'File "', "Exception(")
AST_CODE_FORMAT = re.compile(r"^AST-\d{3}$")


def _flatten_route_paths(routes: list, prefix: str = "") -> list[str]:
    """Caminhos efetivos das rotas, inclusive de routers incluídos.

    A partir do FastAPI 0.16x, ``app.include_router`` guarda um ``_IncludedRouter`` (sem ``path``)
    com ``original_router`` e ``include_context.prefix``; versões antigas copiavam as rotas.
    O helper cobre os dois casos.
    """
    paths: list[str] = []
    for route in routes:
        route_path = getattr(route, "path", None)
        if isinstance(route_path, str):
            paths.append(prefix + route_path)
            continue
        original_router = getattr(route, "original_router", None)
        if original_router is None:
            continue
        include_prefix = getattr(getattr(route, "include_context", None), "prefix", "") or ""
        paths.extend(_flatten_route_paths(original_router.routes, prefix + include_prefix))
    return paths


def _assistant_route_paths(app: FastAPI) -> list[str]:
    return [path for path in _flatten_route_paths(app.routes) if path.startswith(ASSISTANT_PREFIX)]


@pytest.fixture
def disabled_client(settings_override) -> TestClient:
    settings_override(assistant_enabled=False)
    app = FastAPI()
    register_assistant(app)
    return TestClient(app, raise_server_exceptions=False)


# --------------------------------------------------------------------------------------------
# Stub HTTP com a flag desligada
# --------------------------------------------------------------------------------------------
class TestAssistantStubDisabled:
    def test_ask_returns_501(self, disabled_client):
        response = disabled_client.post(ASK_PATH, json={"question": "Qual a conduta?"})
        assert response.status_code == 501

    def test_ask_returns_standard_error_envelope(self, disabled_client):
        body = disabled_client.post(ASK_PATH, json={"question": "Qual a conduta?"}).json()
        assert isinstance(body.get("error"), str) and body["error"].strip()
        assert AST_CODE_FORMAT.match(body.get("code", ""))
        assert is_reserved_code(body["code"]) is True
        assert "data" not in body  # erro não vem no envelope de sucesso

    def test_ask_does_not_leak_stacktrace(self, disabled_client):
        text = disabled_client.post(ASK_PATH, json={"question": "Qual a conduta?"}).text
        for marker in STACKTRACE_MARKERS:
            assert marker not in text

    def test_ask_without_body_still_returns_501(self, disabled_client):
        # Com o assistente desligado, nem a validação do DTO deve rodar: a resposta é 501.
        assert disabled_client.post(ASK_PATH).status_code == 501

    @pytest.mark.parametrize(
        ("method", "path"),
        [("GET", f"{ASSISTANT_PREFIX}/flows"), ("POST", f"{ASSISTANT_PREFIX}/flows/x/resume"), ("GET", ASSISTANT_PREFIX + "/health")],
    )
    def test_any_assistant_route_returns_501(self, disabled_client, method, path):
        response = disabled_client.request(method, path)
        assert response.status_code == 501
        assert AST_CODE_FORMAT.match(response.json().get("code", ""))

    def test_routes_outside_assistant_prefix_are_untouched(self, disabled_client):
        assert disabled_client.get("/api/v1/other").status_code == 404


# --------------------------------------------------------------------------------------------
# register_assistant
# --------------------------------------------------------------------------------------------
class TestRegisterAssistant:
    def test_registers_assistant_routes(self, settings_override):
        settings_override(assistant_enabled=False)
        app = FastAPI()
        register_assistant(app)
        assert _assistant_route_paths(app) != []

    def test_is_idempotent(self, settings_override):
        settings_override(assistant_enabled=False)
        app = FastAPI()
        register_assistant(app)
        first = _assistant_route_paths(app)
        register_assistant(app)
        assert _assistant_route_paths(app) == first

    def test_registers_independently_per_app(self, settings_override):
        settings_override(assistant_enabled=False)
        first_app, second_app = FastAPI(), FastAPI()
        register_assistant(first_app)
        register_assistant(second_app)
        assert _assistant_route_paths(first_app) == _assistant_route_paths(second_app) != []


# --------------------------------------------------------------------------------------------
# init_assistant_resources
# --------------------------------------------------------------------------------------------
class TestInitAssistantResources:
    def test_is_synchronous(self):
        assert not inspect.iscoroutinefunction(init_assistant_resources)

    @pytest.mark.parametrize("is_enabled", [False, True])
    def test_does_not_raise_and_does_not_block(self, settings_override, is_enabled):
        settings_override(assistant_enabled=is_enabled)
        started = time.perf_counter()
        init_assistant_resources()
        assert time.perf_counter() - started < INIT_MAX_SECONDS

    def test_is_idempotent(self, settings_override):
        settings_override(assistant_enabled=False)
        init_assistant_resources()
        init_assistant_resources()


# --------------------------------------------------------------------------------------------
# Configuração inválida (achado I-3 da revisão F0; ARCHITECTURE 5.3, RIPD 5.4)
# Uma configuração inválida desliga o assistente sem derrubar o backend, e o log traz só o
# nome do campo, nunca o valor informado nem a senha da URL do banco.
# --------------------------------------------------------------------------------------------
INVALID_DOCTOR_USERNAME = "a12345678909"  # casa o padrão de CPF: rejeitado pela decisão PA-07
SYNTHETIC_DB_PASSWORD = "senha-sintetica-f0"


@pytest.fixture
def invalid_settings(settings_override, monkeypatch):
    """Ambiente com configuração inválida. Aplicado direto nas variáveis de ambiente, porque o
    ``settings_override`` instancia as settings e a validação lançaria já no setup."""
    import app.assistant.bootstrap as bootstrap
    from app.core import settings as settings_module

    monkeypatch.setattr(bootstrap, "_init_thread", None)
    monkeypatch.setenv("ASSISTANT_ENABLED", "true")
    monkeypatch.setenv("DOCTOR_USERNAME", INVALID_DOCTOR_USERNAME)
    monkeypatch.setenv("DATABASE_URL", f"postgresql://healthai:{SYNTHETIC_DB_PASSWORD}@localhost:5433/healthai")
    settings_module.get_settings.cache_clear()
    return bootstrap


class TestInvalidSettings:
    def test_init_does_not_raise_nor_start_thread(self, invalid_settings):
        init_assistant_resources()
        assert invalid_settings._init_thread is None

    def test_stub_still_answers_501(self, invalid_settings):
        app = FastAPI()
        register_assistant(app)
        response = TestClient(app, raise_server_exceptions=False).post(ASK_PATH)
        assert response.status_code == 501

    def test_log_has_field_name_but_no_values(self, invalid_settings, caplog):
        caplog.set_level("ERROR", logger="app.assistant.bootstrap")
        init_assistant_resources()
        assert "doctor_username" in caplog.text
        assert INVALID_DOCTOR_USERNAME not in caplog.text
        assert SYNTHETIC_DB_PASSWORD not in caplog.text


# --------------------------------------------------------------------------------------------
# Ponto de ligação no app/main.py (inspeção do código, sem importar o app real)
# --------------------------------------------------------------------------------------------
def _parse_main() -> ast.Module:
    return ast.parse(MAIN_PY.read_text(encoding="utf-8"))


def _call_name(node: ast.AST) -> str | None:
    """Nome da função chamada numa instrução ``expr`` (``foo()`` ou ``obj.foo()``)."""
    if not isinstance(node, ast.Expr) or not isinstance(node.value, ast.Call):
        return None
    func = node.value.func
    if isinstance(func, ast.Name):
        return func.id
    if isinstance(func, ast.Attribute):
        return func.attr
    return None


def _lifespan_body(module: ast.Module) -> list[ast.stmt]:
    for node in module.body:
        if isinstance(node, (ast.AsyncFunctionDef, ast.FunctionDef)) and node.name == "lifespan":
            body = list(node.body)
            is_docstring = body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant)
            return body[1:] if is_docstring else body
    raise AssertionError("função lifespan não encontrada em app/main.py")


class TestMainWiring:
    def test_main_imports_bootstrap_functions(self):
        imported = {
            alias.name
            for node in ast.walk(_parse_main())
            if isinstance(node, ast.ImportFrom) and node.module == "app.assistant.bootstrap"
            for alias in node.names
        }
        assert {"register_assistant", "init_assistant_resources"} <= imported

    def test_init_assistant_resources_is_first_statement_of_lifespan(self):
        body = _lifespan_body(_parse_main())
        assert _call_name(body[0]) == "init_assistant_resources"

    def test_init_runs_before_legacy_models_load(self):
        names = [_call_name(statement) for statement in _lifespan_body(_parse_main())]
        assert names.index("init_assistant_resources") < names.index("load_all_models")

    def test_register_assistant_comes_after_every_include_router(self):
        module_statements = _parse_main().body
        include_lines = [node.lineno for node in module_statements if _call_name(node) == "include_router"]
        register_lines = [node.lineno for node in module_statements if _call_name(node) == "register_assistant"]
        assert include_lines, "app/main.py deveria manter os include_router existentes"
        assert len(register_lines) == 1
        assert register_lines[0] > max(include_lines)

    def test_register_assistant_receives_the_app(self):
        for node in _parse_main().body:
            if _call_name(node) != "register_assistant":
                continue
            args = node.value.args
            assert len(args) == 1 and isinstance(args[0], ast.Name) and args[0].id == "app"
            return
        raise AssertionError("register_assistant(app) não encontrado no nível do módulo")

    def test_main_references_assistant_only_through_bootstrap(self):
        source = MAIN_PY.read_text(encoding="utf-8")
        assistant_imports = re.findall(r"from app\.assistant[\w.]*", source)
        assert set(assistant_imports) == {"from app.assistant.bootstrap"}
