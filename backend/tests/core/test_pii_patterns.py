"""
Testes TDD de ``app.core.pii_patterns`` (F0, passo 0.2).

Fonte única da especificação: seção 17 do RIPD (``.agents/docs/privacy/RIPD_assistente_medico.md``).
Cada entidade tem os exemplos positivos (devem casar) e negativos (não devem casar) da ficha.
Todos os valores são SINTÉTICOS (regra geral 6 do RIPD) e nunca são associados a nomes reais.

Fora do escopo destes testes (exigem NER ou módulo próprio, conforme o RIPD):
    - ``M. S. Oliveira`` (nome sem palavra de contexto) e ``residente em Santos/SP`` -> NER (F2).
    - IPv6 (``2001:db8::1``) -> módulo ``ipaddress`` sobre candidatos, não regex.
    - Chave ``AIza…`` -> formato marcado como [A CONFIRMAR] no RIPD.
"""

from __future__ import annotations

import inspect
import re

import pytest

from app.core import pii_patterns
from app.core.pii_patterns import (
    ADDRESS_PATTERN,
    BR_UF_CODES,
    CEP_PATTERN,
    CNS_PATTERN,
    CPF_PATTERN,
    CRM_PATTERN,
    DATE_PATTERN,
    EMAIL_PATTERN,
    IP_PATTERN,
    LICENSE_PLATE_PATTERN,
    MEDICAL_RECORD_PATTERN,
    PATIENT_CODE_PATTERN,
    PERSON_CONTEXT_PATTERN,
    PHONE_BR_PATTERN,
    PII_PATTERNS,
    PLATE_ALLOWLIST,
    PROFESSIONAL_REG_PATTERN,
    RG_PATTERN,
    SECRET_PATTERN,
    is_valid_cns,
    is_valid_cpf,
    is_valid_luhn,
)

# Quantidade de padrões do dicionário, decidida no checkpoint F0 (itens 1–15 da seção 17.2).
EXPECTED_PII_PATTERN_COUNT = 15

# Rótulos sem colchetes que o RIPD define de forma única (seção 17.5).
# Nome de pessoa e endereço têm rótulos variáveis ([PACIENTE_n], [LOCAL_n]…), então são
# verificados pela constante, não pela chave.
UNAMBIGUOUS_LABEL_TO_PATTERN = {
    "CPF": CPF_PATTERN,
    "CNS": CNS_PATTERN,
    "RG": RG_PATTERN,
    "CRM": CRM_PATTERN,
    "TELEFONE": PHONE_BR_PATTERN,
    "EMAIL": EMAIL_PATTERN,
    "CEP": CEP_PATTERN,
    "DATA": DATE_PATTERN,
    "PRONTUARIO": MEDICAL_RECORD_PATTERN,
    "PLACA": LICENSE_PLATE_PATTERN,
    "REGISTRO_PROFISSIONAL": PROFESSIONAL_REG_PATTERN,
    "IP": IP_PATTERN,
    "SEGREDO": SECRET_PATTERN,
}

ALL_PII_CONSTANTS = [
    CPF_PATTERN,
    CNS_PATTERN,
    RG_PATTERN,
    CRM_PATTERN,
    PHONE_BR_PATTERN,
    EMAIL_PATTERN,
    CEP_PATTERN,
    DATE_PATTERN,
    PERSON_CONTEXT_PATTERN,
    ADDRESS_PATTERN,
    MEDICAL_RECORD_PATTERN,
    LICENSE_PLATE_PATTERN,
    PROFESSIONAL_REG_PATTERN,
    IP_PATTERN,
    SECRET_PATTERN,
]

# Ordem de aplicação da regra geral 2 do RIPD (do mais específico ao mais genérico).
# CRM e REGISTRO_PROFISSIONAL estão no mesmo degrau; a ordem entre eles não é verificada.
APPLICATION_ORDER_STEPS = [
    [SECRET_PATTERN],
    [EMAIL_PATTERN],
    [IP_PATTERN],
    [CNS_PATTERN],
    [CPF_PATTERN],
    [PHONE_BR_PATTERN],
    [CEP_PATTERN],
    [RG_PATTERN],
    [CRM_PATTERN, PROFESSIONAL_REG_PATTERN],
    [MEDICAL_RECORD_PATTERN],
    [LICENSE_PLATE_PATTERN],
    [DATE_PATTERN],
    [ADDRESS_PATTERN],
    [PERSON_CONTEXT_PATTERN],
]


def _matches(pattern: re.Pattern[str], text: str) -> bool:
    return pattern.search(text) is not None


def _digits(text: str) -> str:
    return re.sub(r"\D", "", text)


# --------------------------------------------------------------------------------------------
# Estrutura do módulo
# --------------------------------------------------------------------------------------------
class TestModuleStructure:
    def test_all_constants_are_compiled_patterns(self):
        for pattern in [*ALL_PII_CONSTANTS, PATIENT_CODE_PATTERN]:
            assert isinstance(pattern, re.Pattern)

    def test_pii_patterns_is_dict_of_compiled_patterns(self):
        assert isinstance(PII_PATTERNS, dict)
        assert all(isinstance(key, str) for key in PII_PATTERNS)
        assert all(isinstance(value, re.Pattern) for value in PII_PATTERNS.values())

    def test_pii_patterns_has_exactly_15_entries(self):
        assert len(PII_PATTERNS) == EXPECTED_PII_PATTERN_COUNT

    def test_pii_patterns_contains_every_entity_constant(self):
        values = list(PII_PATTERNS.values())
        for pattern in ALL_PII_CONSTANTS:
            assert any(value is pattern for value in values), pattern.pattern[:40]

    @pytest.mark.parametrize("label", sorted(UNAMBIGUOUS_LABEL_TO_PATTERN))
    def test_keys_are_labels_without_brackets(self, label):
        assert label in PII_PATTERNS
        assert PII_PATTERNS[label] is UNAMBIGUOUS_LABEL_TO_PATTERN[label]

    def test_keys_have_no_brackets(self):
        assert all("[" not in key and "]" not in key for key in PII_PATTERNS)

    def test_insertion_order_follows_application_order(self):
        values = list(PII_PATTERNS.values())

        def position(pattern: re.Pattern[str]) -> int:
            return next(index for index, value in enumerate(values) if value is pattern)

        step_positions = [[position(pattern) for pattern in step] for step in APPLICATION_ORDER_STEPS]
        for previous_step, next_step in zip(step_positions, step_positions[1:]):
            assert max(previous_step) < min(next_step)

    def test_patient_code_pattern_is_outside_pii_patterns(self):
        assert all(value is not PATIENT_CODE_PATTERN for value in PII_PATTERNS.values())
        assert "PATIENT_CODE" not in PII_PATTERNS

    def test_module_does_not_import_heavy_nlp(self):
        source = inspect.getsource(pii_patterns)
        assert "import spacy" not in source
        assert "from spacy" not in source

    def test_br_uf_codes_has_27_federative_units(self):
        assert len(BR_UF_CODES) == 27
        for uf in ("SP", "RJ", "MG", "DF", "AC", "TO"):
            assert uf in BR_UF_CODES


# --------------------------------------------------------------------------------------------
# 1. CPF
# --------------------------------------------------------------------------------------------
class TestCPF:
    @pytest.mark.parametrize(
        "text", ["123.456.789-09", "12345678909", "529.982.247-25", "CPF: 111.444.777-35"]
    )
    def test_positive_examples_match(self, text):
        assert _matches(CPF_PATTERN, text)

    @pytest.mark.parametrize("text", ["123.456.789", "1234567890123456", "12.345.678/0001-95"])
    def test_negative_examples_do_not_match(self, text):
        assert not _matches(CPF_PATTERN, text)

    def test_repeated_digits_match_by_format_but_are_invalid(self):
        # RIPD: ainda mascarado pelo formato; só o dígito verificador é inválido.
        assert _matches(CPF_PATTERN, "111.111.111-11")
        assert is_valid_cpf("11111111111") is False

    @pytest.mark.parametrize("text", ["123.456.789-09", "529.982.247-25", "111.444.777-35"])
    def test_check_digits_are_valid(self, text):
        assert is_valid_cpf(_digits(text)) is True

    @pytest.mark.parametrize("digits", ["12345678900", "52998224726", "00000000000", "1234567890"])
    def test_invalid_check_digits_or_length_are_rejected(self, digits):
        assert is_valid_cpf(digits) is False


# --------------------------------------------------------------------------------------------
# 2. CNS
# --------------------------------------------------------------------------------------------
class TestCNS:
    @pytest.mark.parametrize("text", ["898 0012 3456 7891", "898001234567891", "700000000000005"])
    def test_positive_examples_match(self, text):
        assert _matches(CNS_PATTERN, text)

    @pytest.mark.parametrize("text", ["398 0012 3456 7891", "8980012345678"])
    def test_negative_examples_do_not_match(self, text):
        assert not _matches(CNS_PATTERN, text)

    def test_invalid_checksum_matches_by_format_but_is_invalid(self):
        assert _matches(CNS_PATTERN, "898 0012 3456 7890")
        assert is_valid_cns("898001234567890") is False

    @pytest.mark.parametrize("text", ["898 0012 3456 7891", "700000000000005"])
    def test_weighted_sum_is_valid(self, text):
        assert is_valid_cns(_digits(text)) is True

    def test_wrong_length_is_invalid(self):
        assert is_valid_cns("8980012345678") is False


# --------------------------------------------------------------------------------------------
# 3. RG
# --------------------------------------------------------------------------------------------
class TestRG:
    @pytest.mark.parametrize(
        "text", ["12.345.678-9", "RG 12.345.678-X", "identidade nº 123456789", "RG: 1.234.567"]
    )
    def test_positive_examples_match(self, text):
        assert _matches(RG_PATTERN, text)

    @pytest.mark.parametrize(
        "text", ["contagem de 12.345.678 células", "123456789", "1.234 mg"]
    )
    def test_negative_examples_do_not_match(self, text):
        assert not _matches(RG_PATTERN, text)


# --------------------------------------------------------------------------------------------
# 4. CRM
# --------------------------------------------------------------------------------------------
class TestCRM:
    @pytest.mark.parametrize("text", ["CRM-SP 123456", "CRM 54321/RJ", "CRM/MG 98765", "crm 123456"])
    def test_positive_examples_match(self, text):
        assert _matches(CRM_PATTERN, text)

    @pytest.mark.parametrize("text", ["o CRM regula a profissão", "CRM-SP", "123456/SP"])
    def test_negative_examples_do_not_match(self, text):
        assert not _matches(CRM_PATTERN, text)


# --------------------------------------------------------------------------------------------
# 5. Telefone BR
# --------------------------------------------------------------------------------------------
class TestPhoneBR:
    @pytest.mark.parametrize(
        "text", ["(11) 98888-7777", "+55 21 3333-4444", "11988887777", "tel: 98888-7777"]
    )
    def test_positive_examples_match(self, text):
        assert _matches(PHONE_BR_PATTERN, text)

    @pytest.mark.parametrize(
        "text", ["(00) 98888-7777", "0800 123 4567", "98888-7777", "120/80 mmHg"]
    )
    def test_negative_examples_do_not_match(self, text):
        assert not _matches(PHONE_BR_PATTERN, text)


# --------------------------------------------------------------------------------------------
# 6. E-mail
# --------------------------------------------------------------------------------------------
class TestEmail:
    @pytest.mark.parametrize(
        "text",
        ["maria.silva@example.com", "dr.joao+agenda@hospital.example.org", "PACIENTE_01@EXAMPLE.COM.BR"],
    )
    def test_positive_examples_match_the_whole_address(self, text):
        match = EMAIL_PATTERN.search(text)
        assert match is not None
        assert match.group(0) == text  # mascarar por inteiro, sem preservar o domínio

    @pytest.mark.parametrize("text", ["maria@", "@hospital", "5 mg @ 8h", "usuario@localhost"])
    def test_negative_examples_do_not_match(self, text):
        assert not _matches(EMAIL_PATTERN, text)


# --------------------------------------------------------------------------------------------
# 7. CEP
# --------------------------------------------------------------------------------------------
class TestCEP:
    @pytest.mark.parametrize("text", ["01001-000", "CEP 01001000", "CEP: 20.040-020"])
    def test_positive_examples_match(self, text):
        assert _matches(CEP_PATTERN, text)

    @pytest.mark.parametrize("text", ["01001000", "1234-567", "12345-67"])
    def test_negative_examples_do_not_match(self, text):
        assert not _matches(CEP_PATTERN, text)


# --------------------------------------------------------------------------------------------
# 8. Data
# --------------------------------------------------------------------------------------------
class TestDate:
    @pytest.mark.parametrize(
        "text", ["12/03/1985", "1985-03-12", "12 de março de 1985", "05.11.24", "12 de março"]
    )
    def test_positive_examples_match(self, text):
        assert _matches(DATE_PATTERN, text)

    @pytest.mark.parametrize(
        "text",
        [
            "120/80",
            "10-20-30 mg",
            "BI-RADS 4",
            "2/3 dos casos",
            "há 45 dias",
            "conforme a diretriz de 2023",  # ano isolado é preservado (citações, P-041)
        ],
    )
    def test_negative_examples_do_not_match(self, text):
        assert not _matches(DATE_PATTERN, text)


# --------------------------------------------------------------------------------------------
# 9. Nome de pessoa (só a parte regex; nome sem contexto exige NER)
# --------------------------------------------------------------------------------------------
class TestPersonContext:
    @pytest.mark.parametrize(
        ("text", "name"),
        [
            ("Paciente Maria Silva", "Maria Silva"),
            ("Dra. Ana Paula de Souza", "Ana Paula de Souza"),
            ("mãe: Joana dos Santos", "Joana dos Santos"),
        ],
    )
    def test_positive_examples_capture_the_name(self, text, name):
        match = PERSON_CONTEXT_PATTERN.search(text)
        assert match is not None
        assert name in match.group(0)

    @pytest.mark.parametrize(
        "text",
        [
            "doença de Paget",
            "critérios de Rotterdam",
            "exame de Papanicolaou",
            "BRCA1",
            "Paciente refere dor",  # palavra seguinte não é nome (minúscula)
        ],
    )
    def test_negative_examples_do_not_match(self, text):
        assert not _matches(PERSON_CONTEXT_PATTERN, text)


# --------------------------------------------------------------------------------------------
# 10. Endereço (só logradouro; bairro/município exigem NER)
# --------------------------------------------------------------------------------------------
class TestAddress:
    @pytest.mark.parametrize("text", ["Rua das Flores, 123, apto 45", "Av. Brasil, nº 1500"])
    def test_positive_examples_match(self, text):
        assert _matches(ADDRESS_PATTERN, text)

    @pytest.mark.parametrize(
        "text", ["critérios de Rotterdam", "sistema Bethesda", "via oral", "quadrante superior externo"]
    )
    def test_negative_examples_do_not_match(self, text):
        assert not _matches(ADDRESS_PATTERN, text)


# --------------------------------------------------------------------------------------------
# 11. Prontuário / registro hospitalar / carteirinha
# --------------------------------------------------------------------------------------------
class TestMedicalRecord:
    @pytest.mark.parametrize(
        "text",
        ["Prontuário nº 0045871", "RH: 123.456-7", "matrícula 2024/000123", "carteirinha 0012 3456 7890"],
    )
    def test_positive_examples_match(self, text):
        assert _matches(MEDICAL_RECORD_PATTERN, text)

    @pytest.mark.parametrize(
        "text", ["registro de enfermagem", "RH negativo", "atendimento ambulatorial", "PAC-001"]
    )
    def test_negative_examples_do_not_match(self, text):
        assert not _matches(MEDICAL_RECORD_PATTERN, text)


# --------------------------------------------------------------------------------------------
# 12. Placa de veículo
# --------------------------------------------------------------------------------------------
class TestLicensePlate:
    @pytest.mark.parametrize("text", ["ABC-1234", "ABC1234", "ABC1D23"])
    def test_positive_examples_match(self, text):
        assert _matches(LICENSE_PLATE_PATTERN, text)

    @pytest.mark.parametrize("text", ["CID-10", "HER2", "ABC-123", "abc1234"])
    def test_negative_examples_do_not_match(self, text):
        assert not _matches(LICENSE_PLATE_PATTERN, text)

    @pytest.mark.parametrize("text", ["TNM2017", "WHO2019"])
    def test_known_false_positive_is_matched_by_format(self, text):
        # Falso positivo conhecido: sigla + ano casa o formato antigo; quem filtra é a allowlist.
        assert _matches(LICENSE_PLATE_PATTERN, text)

    @pytest.mark.parametrize("acronym", ["TNM", "WHO", "OMS", "CID", "ACR", "FIGO"])
    def test_plate_allowlist_contains_clinical_acronyms(self, acronym):
        assert acronym in PLATE_ALLOWLIST

    @pytest.mark.parametrize("text", ["TNM2017", "WHO2019"])
    def test_known_false_positive_is_covered_by_allowlist(self, text):
        match = LICENSE_PLATE_PATTERN.search(text)
        assert match is not None
        assert match.group(0)[:3] in PLATE_ALLOWLIST

    def test_real_plate_prefix_is_not_in_allowlist(self):
        assert "ABC" not in PLATE_ALLOWLIST


# --------------------------------------------------------------------------------------------
# 13. Outros registros profissionais
# --------------------------------------------------------------------------------------------
class TestProfessionalRegistration:
    @pytest.mark.parametrize("text", ["COREN-SP 123456", "CRF/RJ 12345", "CRP 06/12345"])
    def test_positive_examples_match(self, text):
        assert _matches(PROFESSIONAL_REG_PATTERN, text)

    @pytest.mark.parametrize("text", ["CRF", "CRP elevada", "PCR 12 mg/L"])
    def test_negative_examples_do_not_match(self, text):
        assert not _matches(PROFESSIONAL_REG_PATTERN, text)


# --------------------------------------------------------------------------------------------
# 14. Endereço IP (IPv4 por regex; IPv6 fica com o módulo ipaddress)
# --------------------------------------------------------------------------------------------
class TestIP:
    @pytest.mark.parametrize("text", ["203.0.113.45", "198.51.100.7"])
    def test_positive_examples_match(self, text):
        assert _matches(IP_PATTERN, text)

    @pytest.mark.parametrize("text", ["1.2.3", "999.1.1.1", "10.5.2.1.4"])
    def test_negative_examples_do_not_match(self, text):
        assert not _matches(IP_PATTERN, text)


# --------------------------------------------------------------------------------------------
# 15. Segredos
# --------------------------------------------------------------------------------------------
class TestSecret:
    @pytest.mark.parametrize(
        "text",
        [
            "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJtZWRpY28ifQ.c2lnbmF0dXJlX2Zha2U",
            "password=Exemplo#123",
            "postgresql://usuario:senha@host.example:6543/postgres",
            "4111 1111 1111 1111",
        ],
    )
    def test_positive_examples_match(self, text):
        assert _matches(SECRET_PATTERN, text)

    @pytest.mark.parametrize("text", ["token de acesso expirado", "eyJ"])
    def test_negative_examples_do_not_match(self, text):
        assert not _matches(SECRET_PATTERN, text)

    def test_card_number_passes_luhn(self):
        assert is_valid_luhn("4111111111111111") is True

    def test_card_like_number_failing_luhn_is_rejected(self):
        # Casa o formato, mas falha no Luhn: não é rotulado como cartão.
        assert is_valid_luhn("1234567890123456") is False


# --------------------------------------------------------------------------------------------
# 16. Código interno do paciente (não é mascarado; decide o fallback, P-051)
# --------------------------------------------------------------------------------------------
class TestPatientCode:
    @pytest.mark.parametrize("text", ["PAC-001", "paciente PAC-0420"])
    def test_positive_examples_match(self, text):
        assert _matches(PATIENT_CODE_PATTERN, text)

    @pytest.mark.parametrize("text", ["PAC-1", "PACS", "IMPAC-001"])
    def test_negative_examples_do_not_match(self, text):
        assert not _matches(PATIENT_CODE_PATTERN, text)

    def test_patient_code_is_not_matched_by_any_pii_pattern(self):
        offending = [label for label, pattern in PII_PATTERNS.items() if pattern.search("PAC-001")]
        assert offending == []
