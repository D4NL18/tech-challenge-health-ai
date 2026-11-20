"""
Testes TDD de ``app.assistant.errors`` (F0, passo 0.3).

Contrato (ARCHITECTURE.md, seção 4.4, e regra global de tratamento de erros):
    - ``AssistantDomainError(code, http_status, public_message)`` é a base de toda exceção de
      domínio do assistente; herda de ``Exception`` e expõe os três atributos.
    - ``code`` segue ``AST-NNN`` (prefixo de três letras + número) e cai numa faixa reservada.
    - ``http_status`` é de erro (4xx ou 5xx): nada de "falso 200".
    - Faixas reservadas por fase em ``AST_CODE_RANGES`` (números, sem o prefixo):
        F4    -> AST-4xx      (400…499, prontuário)
        F5    -> AST-001…019  (guardrails, auditoria)
        F7_F8 -> AST-020…049  (LLM, fluxos)
        F9    -> AST-050…069  (API, auth, seleção de modelo)
    - ``is_reserved_code(code) -> bool`` diz se o código tem formato válido e está numa faixa.
"""

from __future__ import annotations

import pytest

from app.assistant.errors import AST_CODE_RANGES, AssistantDomainError, is_reserved_code

EXPECTED_RANGES = {
    "F4": range(400, 500),
    "F5": range(1, 20),
    "F7_F8": range(20, 50),
    "F9": range(50, 70),
}


class TestAssistantDomainError:
    def test_is_an_exception(self):
        assert issubclass(AssistantDomainError, Exception)

    def test_positional_construction_exposes_attributes(self):
        error = AssistantDomainError("AST-404", 404, "Paciente não encontrado.")
        assert error.code == "AST-404"
        assert error.http_status == 404
        assert error.public_message == "Paciente não encontrado."

    def test_keyword_construction(self):
        error = AssistantDomainError(
            code="AST-022", http_status=503, public_message="Modelo carregando; tente em instantes."
        )
        assert (error.code, error.http_status) == ("AST-022", 503)

    def test_can_be_raised_and_caught_as_domain_error(self):
        with pytest.raises(AssistantDomainError) as caught:
            raise AssistantDomainError("AST-020", 404, "Fluxo não encontrado.")
        assert caught.value.code == "AST-020"

    def test_subclass_is_caught_by_base_class(self):
        class PatientNotFoundError(AssistantDomainError):
            pass

        with pytest.raises(AssistantDomainError):
            raise PatientNotFoundError("AST-404", 404, "Paciente não encontrado.")

    @pytest.mark.parametrize("bad_code", ["AST-1", "AST-0001", "ast-404", "FIN-001", "AST404", "", "AST-ABC"])
    def test_malformed_code_is_rejected(self, bad_code):
        with pytest.raises(ValueError):
            AssistantDomainError(bad_code, 400, "Erro.")

    @pytest.mark.parametrize("unreserved_code", ["AST-000", "AST-070", "AST-150", "AST-399", "AST-500"])
    def test_code_outside_reserved_ranges_is_rejected(self, unreserved_code):
        with pytest.raises(ValueError):
            AssistantDomainError(unreserved_code, 400, "Erro.")

    @pytest.mark.parametrize("non_error_status", [200, 201, 302, 399, 600])
    def test_non_error_http_status_is_rejected(self, non_error_status):
        with pytest.raises(ValueError):
            AssistantDomainError("AST-001", non_error_status, "Erro.")


class TestReservedRanges:
    def test_ranges_match_architecture(self):
        assert dict(AST_CODE_RANGES) == EXPECTED_RANGES

    def test_ranges_do_not_overlap(self):
        seen: set[int] = set()
        for numbers in AST_CODE_RANGES.values():
            assert seen.isdisjoint(numbers)
            seen.update(numbers)

    @pytest.mark.parametrize(
        "code",
        ["AST-001", "AST-019", "AST-020", "AST-022", "AST-049", "AST-050", "AST-051", "AST-069", "AST-400", "AST-404", "AST-499"],
    )
    def test_boundaries_inside_ranges_are_reserved(self, code):
        assert is_reserved_code(code) is True

    @pytest.mark.parametrize("code", ["AST-000", "AST-070", "AST-399", "AST-500", "FIN-001", "AST-4", "qualquer"])
    def test_outside_or_malformed_is_not_reserved(self, code):
        assert is_reserved_code(code) is False

    @pytest.mark.parametrize(
        ("code", "phase"),
        [("AST-404", "F4"), ("AST-001", "F5"), ("AST-021", "F7_F8"), ("AST-052", "F9")],
    )
    def test_known_codes_fall_in_owner_phase(self, code, phase):
        number = int(code.split("-")[1])
        assert number in AST_CODE_RANGES[phase]
