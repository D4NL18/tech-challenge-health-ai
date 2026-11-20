"""
==================================================================================================
MÓDULO: app/core/pii_patterns.py — Lista oficial de entidades PII pt-BR (fonte única)
==================================================================================================
Objetivo:
    Concentrar, num único lugar, as expressões regulares e as validações de dígito verificador das
    entidades PII definidas na seção 17 do RIPD (`.agents/docs/privacy/RIPD_assistente_medico.md`).
    Consumidores:
      - F2: anonimizador do dataset e `PIIGate` (P-047);
      - F5: `pii_masker` de logs e auditoria (P-044);
      - F7: detecção de `PATIENT_CODE_PATTERN` para decidir o fallback de contingência (P-051).

Regras (RIPD 17.1 e 17.5):
    - Fronteiras numéricas com lookaround (`(?<!\\d)` / `(?!\\d)`), não com `\\b`.
    - `PII_PATTERNS` segue a ORDEM DE APLICAÇÃO da regra geral 2 (mais específico → mais genérico),
      com chaves iguais ao rótulo sem colchetes (`"CPF"`, `"TELEFONE"`...).
    - `PATIENT_CODE_PATTERN` fica FORA de `PII_PATTERNS`: é pseudônimo, não é mascarado.
    - Validação de dígito verificador aumenta a confiança, mas NÃO libera: o que tem formato de
      identificador é tratado mesmo com dígito inválido (regra geral 3).
    - Este módulo não importa spaCy nem nada pesado (é carregado em produção) e NUNCA registra em
      log o texto que examina. O NER vive em `finetuning/preprocessing/anonymizer.py` (F2).

Limitações conhecidas (entidades que o RIPD diz exigirem NER):
    - `PERSON_CONTEXT_PATTERN` só detecta nomes precedidos de palavra de contexto (paciente, Dr.,
      mãe...). Nomes soltos (ex.: "M. S. Oliveira, 54 anos") dependem do NER `PER` da F2.
    - `ADDRESS_PATTERN` só detecta logradouros; bairro, município e instituição dependem do NER `LOC`.
==================================================================================================
"""

from __future__ import annotations

import ipaddress
import re
from typing import Final

# ------------------------------------------------------------------------------------------------
# Conjuntos de apoio às validações
# ------------------------------------------------------------------------------------------------

# 27 unidades federativas: valida a UF opcional de CRM e de outros registros profissionais.
BR_UF_CODES: Final[frozenset[str]] = frozenset({
    "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", "MG", "PA",
    "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO",
})

# DDDs válidos no Brasil (Anatel). Uso opcional para reduzir falso positivo de telefone.
BR_DDD_CODES: Final[frozenset[str]] = frozenset({
    "11", "12", "13", "14", "15", "16", "17", "18", "19",
    "21", "22", "24", "27", "28",
    "31", "32", "33", "34", "35", "37", "38",
    "41", "42", "43", "44", "45", "46", "47", "48", "49",
    "51", "53", "54", "55",
    "61", "62", "63", "64", "65", "66", "67", "68", "69",
    "71", "73", "74", "75", "77", "79",
    "81", "82", "83", "84", "85", "86", "87", "88", "89",
    "91", "92", "93", "94", "95", "96", "97", "98", "99",
})

# Siglas clínicas que, seguidas de ano (TNM2017, WHO2019), casam com o formato antigo de placa.
# Achado cujo prefixo está aqui não é mascarado nem reprova o registro no PIIGate (RIPD item 12).
PLATE_ALLOWLIST: Final[frozenset[str]] = frozenset({"TNM", "WHO", "OMS", "CID", "ACR", "FIGO"})

CPF_LENGTH: Final[int] = 11
CNS_LENGTH: Final[int] = 15
CNS_DIVISOR: Final[int] = 11
LUHN_MIN_LENGTH: Final[int] = 13
LUHN_MAX_LENGTH: Final[int] = 19

# ------------------------------------------------------------------------------------------------
# 1. CPF — máscara NNN.NNN.NNN-NN, sem máscara ou máscara parcial. Validação: is_valid_cpf.
# ------------------------------------------------------------------------------------------------
CPF_PATTERN: Final[re.Pattern[str]] = re.compile(
    r"(?<!\d)\d{3}[.\s]?\d{3}[.\s]?\d{3}[-\s]?\d{2}(?!\d)"
)

# ------------------------------------------------------------------------------------------------
# 2. CNS — 15 dígitos; 1/2 (definitivo) ou 7/8/9 (provisório). Validação: is_valid_cns.
# ------------------------------------------------------------------------------------------------
CNS_PATTERN: Final[re.Pattern[str]] = re.compile(
    r"(?<!\d)[12789]\d{2}\s?\d{4}\s?\d{4}\s?\d{4}(?!\d)"
)

# ------------------------------------------------------------------------------------------------
# 3. RG — sem padrão nacional. Com máscara NN.NNN.NNN-D, ou sem máscara SOMENTE com contexto.
#    Inclui o órgão emissor adjacente (ex.: "SSP/SP"), como pede o RIPD.
# ------------------------------------------------------------------------------------------------
_RG_ISSUER = r"(?:\s*[-/]?\s*(?:SSP|SESP|SDS|SSPDS|SJS|SEJUSP|DETRAN|IFP|IGP|PC)\s*[-/]\s*[A-Z]{2})?"
RG_PATTERN: Final[re.Pattern[str]] = re.compile(
    r"(?:(?<!\d)\d{1,2}\.\d{3}\.\d{3}-?[\dX](?![\w])"
    r"|\b(?:RG|R\.G\.|identidade|c[ée]dula\s+de\s+identidade)\b\s*(?:n[ºo°.]?\s*)?:?\s*"
    r"\d[\d.]{5,11}-?[\dX]?)"
    + _RG_ISSUER,
    re.IGNORECASE,
)

# ------------------------------------------------------------------------------------------------
# 4. CRM — prefixo obrigatório; UF opcional antes ou depois do número.
# ------------------------------------------------------------------------------------------------
CRM_PATTERN: Final[re.Pattern[str]] = re.compile(
    r"\bCRM\s*[-/]?\s*(?:[A-Z]{2}\s*[-/]?\s*)?\d{4,7}(?:\s*[-/]\s*[A-Z]{2})?\b",
    re.IGNORECASE,
)

# ------------------------------------------------------------------------------------------------
# 5. Telefone BR — com DDD (celular 9 dígitos começando em 9; fixo 8 dígitos começando em 2–5),
#    ou sem DDD SOMENTE com palavra de contexto (tel, cel, whatsapp...).
# ------------------------------------------------------------------------------------------------
PHONE_BR_PATTERN: Final[re.Pattern[str]] = re.compile(
    r"(?<!\d)(?:\+?55[\s-]?)?\(?0?[1-9]{2}\)?[\s-]?(?:9\d{4}|[2-5]\d{3})[\s-]?\d{4}(?!\d)"
    r"|\b(?:tel|telefone|cel|celular|whats(?:app)?|fone|contato)\b\.?\s*:?\s*"
    r"(?:9\d{4}|[2-5]\d{3})[\s-]?\d{4}(?!\d)",
    re.IGNORECASE,
)

# ------------------------------------------------------------------------------------------------
# 6. E-mail — validação apenas sintática (sem DNS).
# ------------------------------------------------------------------------------------------------
EMAIL_PATTERN: Final[re.Pattern[str]] = re.compile(
    r"[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}"
)

# ------------------------------------------------------------------------------------------------
# 7. CEP — NNNNN-NNN / NN.NNN-NNN; oito dígitos contínuos só com a palavra "CEP".
# ------------------------------------------------------------------------------------------------
CEP_PATTERN: Final[re.Pattern[str]] = re.compile(
    r"(?<!\d)\d{2}\.?\d{3}-\d{3}(?!\d)"
    r"|\bCEP\b\s*:?\s*\d{5}-?\d{3}(?!\d)",
    re.IGNORECASE,
)

# ------------------------------------------------------------------------------------------------
# 8. Data — dd/mm/aaaa (e variantes), ISO aaaa-mm-dd, por extenso. Ano isolado NÃO é tratado
#    (ano de publicação de protocolo é necessário às citações, P-041).
# ------------------------------------------------------------------------------------------------
_MONTHS_PT = r"(?:janeiro|fevereiro|mar[çc]o|abril|maio|junho|julho|agosto|setembro|outubro|novembro|dezembro)"
DATE_PATTERN: Final[re.Pattern[str]] = re.compile(
    r"(?<!\d)(?:0?[1-9]|[12]\d|3[01])[/.-](?:0?[1-9]|1[0-2])[/.-](?:\d{4}|\d{2})(?!\d)"
    r"|(?<!\d)(?:19|20)\d{2}-(?:0[1-9]|1[0-2])-(?:0[1-9]|[12]\d|3[01])(?!\d)"
    r"|\b(?:0?[1-9]|[12]\d|3[01])º?\s+de\s+" + _MONTHS_PT + r"(?:\s+de\s+\d{4})?\b",
    re.IGNORECASE,
)

# ------------------------------------------------------------------------------------------------
# 9. Nome de pessoa — padrão AUXILIAR de contexto. A detecção principal é o NER `PER` (F2).
#    A palavra de contexto é case-insensitive; o grupo 1 (o nome) EXIGE inicial maiúscula, por
#    isso a flag fica restrita ao trecho de contexto (`(?i:...)`).
# ------------------------------------------------------------------------------------------------
_NAME_TOKEN = r"(?:[A-ZÀ-Ý][a-zà-ÿ]+|[A-Z]\.)"
PERSON_CONTEXT_PATTERN: Final[re.Pattern[str]] = re.compile(
    r"(?i:\b(?:paciente|pcte|sr\.?|sra\.?|dr\.?|dra\.?|enf\.?|m[ãa]e|pai|filh[oa]|acompanhante"
    r"|respons[áa]vel))\s*:?\s+"
    # Ajuste sobre a regex de referência (permitido pelo RIPD 17.1, item 7): a partícula (de, da,
    # dos, e) pode aparecer entre quaisquer dois nomes, e o grupo não captura espaço final.
    r"(" + _NAME_TOKEN + r"(?:(?:\s+(?:d[aeo]s?|e))?\s+" + _NAME_TOKEN + r"){0,4})"
)

# ------------------------------------------------------------------------------------------------
# 10. Endereço — só logradouro (+ número e complemento). Bairro/município/instituição: NER `LOC`.
# ------------------------------------------------------------------------------------------------
ADDRESS_PATTERN: Final[re.Pattern[str]] = re.compile(
    r"\b(?:rua|r\.|avenida|av\.?|travessa|tv\.|alameda|al\.|rodovia|rod\.|estrada|pra[çc]a|largo"
    r"|quadra|qd\.?)\s+[^,\n]{2,60}(?:,\s*(?:n[ºo°.]?\s*)?\d{1,5})?"
    r"(?:\s*,?\s*(?:apto?\.?|apartamento|bloco|casa|sala|cj\.?)\s*\w{1,6})?",
    re.IGNORECASE,
)

# ------------------------------------------------------------------------------------------------
# 11. Prontuário / registro hospitalar / carteirinha — contexto obrigatório. Nunca casa o
#     pseudônimo PAC-NNN (lookahead negativo), e aceita grupos de dígitos separados por espaço.
# ------------------------------------------------------------------------------------------------
MEDICAL_RECORD_PATTERN: Final[re.Pattern[str]] = re.compile(
    r"\b(?:prontu[áa]rio|registro(?:\s+hospitalar)?|RH|matr[íi]cula|atendimento|interna[çc][ãa]o"
    r"|carteirinha|carteira\s+do\s+conv[êe]nio|conv[êe]nio)\s*(?:n[ºo°.]?|n[úu]mero|\#)?\s*:?\s*"
    r"(?!PAC-\d)[A-Z]{0,3}[-\s]?\d(?:[\d.\-/]|\s(?=\d)){3,17}",
    re.IGNORECASE,
)

# ------------------------------------------------------------------------------------------------
# 12. Placa — antiga AAA-9999/AAA9999 e Mercosul AAA9A99. Somente MAIÚSCULAS (sem IGNORECASE).
#     Falso positivo conhecido (TNM2017): filtrar com `is_allowlisted_plate`.
# ------------------------------------------------------------------------------------------------
LICENSE_PLATE_PATTERN: Final[re.Pattern[str]] = re.compile(
    r"(?<![A-Za-z0-9])(?:[A-Z]{3}-?\d{4}|[A-Z]{3}\d[A-Z]\d{2})(?![A-Za-z0-9])"
)

# ------------------------------------------------------------------------------------------------
# 13. Outros registros profissionais (COREN, CRF, CRO, CRP, CREFITO, CRN...) — prefixo obrigatório.
# ------------------------------------------------------------------------------------------------
PROFESSIONAL_REG_PATTERN: Final[re.Pattern[str]] = re.compile(
    r"\b(?:COREN|CRF|CRO|CRP|CREFITO|CRN|CRBM|CRFA|CRESS|CRTR)\s*[-/]?\s*(?:[A-Z]{2}|\d{1,2})?\s*[-/]?\s*"
    r"\d{2,3}\.?\d{3}(?:\s*[-/]\s*[A-Z]{1,3})?\b",
    re.IGNORECASE,
)

# ------------------------------------------------------------------------------------------------
# 14. Endereço IP — IPv4 com octetos 0–255; IPv6 por CANDIDATO (exige "::" ou dígito hexadecimal
#     com letra, para não casar horários como 10:30:00) a confirmar com `is_valid_ip`.
# ------------------------------------------------------------------------------------------------
_IPV4 = r"(?<![\d.])(?:(?:25[0-5]|2[0-4]\d|1?\d?\d)\.){3}(?:25[0-5]|2[0-4]\d|1?\d?\d)(?![\d.])"
_IPV6_CANDIDATE = (
    r"(?<![\w:])(?=[0-9A-Fa-f:]*(?:::|[A-Fa-f]))(?:[0-9A-Fa-f]{0,4}:){2,7}[0-9A-Fa-f]{1,4}(?![\w:])"
)
IP_PATTERN: Final[re.Pattern[str]] = re.compile(_IPV4 + "|" + _IPV6_CANDIDATE)

# ------------------------------------------------------------------------------------------------
# 15. Segredos — JWT, Bearer, chave=valor sensível, URL do Postgres com senha, chave Google,
#     número de cartão. A última alternativa (cartão) só deve ser rotulada como segredo se passar
#     no Luhn (`is_valid_luhn`); se falhar e casar com CNS/CPF, segue a regra daquela entidade.
#     Os consumidores podem usar `CARD_NUMBER_PATTERN` para isolar esse caso.
# ------------------------------------------------------------------------------------------------
_CARD_NUMBER = r"(?<!\d)\d(?:[ -]?\d){12,18}(?!\d)"
CARD_NUMBER_PATTERN: Final[re.Pattern[str]] = re.compile(_CARD_NUMBER)
SECRET_PATTERN: Final[re.Pattern[str]] = re.compile(
    r"eyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}"
    r"|\bBearer\s+[A-Za-z0-9._~+/=-]{16,}"
    r"|\b(?:senha|password|passwd|secret|token|api[_-]?key|authorization)\b\s*[:=]\s*\S+"
    r"|\bpostgres(?:ql)?://[^\s:@]+:[^\s@]+@\S+"
    r"|AIza[0-9A-Za-z_-]{35}"
    r"|" + _CARD_NUMBER,
    re.IGNORECASE,
)

# ------------------------------------------------------------------------------------------------
# 16. Código interno do paciente (pseudônimo). NÃO é mascarado; sua presença bloqueia o fallback
#     para o Gemini e o cache de respostas (P-051). Por isso fica fora de PII_PATTERNS.
# ------------------------------------------------------------------------------------------------
PATIENT_CODE_PATTERN: Final[re.Pattern[str]] = re.compile(r"(?<![A-Za-z0-9])PAC-\d{3,6}(?!\d)")

# ------------------------------------------------------------------------------------------------
# Dicionário oficial — ordem de inserção = ordem de aplicação (RIPD 17.1, regra geral 2).
# Chave = rótulo sem colchetes. As entidades de NER (nome/localidade) entram pelo padrão auxiliar.
# ------------------------------------------------------------------------------------------------
PII_PATTERNS: Final[dict[str, re.Pattern[str]]] = {
    "SEGREDO": SECRET_PATTERN,
    "EMAIL": EMAIL_PATTERN,
    "IP": IP_PATTERN,
    "CNS": CNS_PATTERN,
    "CPF": CPF_PATTERN,
    "TELEFONE": PHONE_BR_PATTERN,
    "CEP": CEP_PATTERN,
    "RG": RG_PATTERN,
    "CRM": CRM_PATTERN,
    "REGISTRO_PROFISSIONAL": PROFESSIONAL_REG_PATTERN,
    "PRONTUARIO": MEDICAL_RECORD_PATTERN,
    "PLACA": LICENSE_PLATE_PATTERN,
    "DATA": DATE_PATTERN,
    "ENDERECO": ADDRESS_PATTERN,
    "PESSOA": PERSON_CONTEXT_PATTERN,
}


# ------------------------------------------------------------------------------------------------
# Validações puras (sem efeito colateral, sem log)
# ------------------------------------------------------------------------------------------------
def _only_digits(value: str) -> str:
    """Remove máscara (pontos, hífens, espaços) e devolve apenas os dígitos."""
    return "".join(char for char in value if char.isdigit())


def _cpf_check_digit(digits: str, first_weight: int) -> int:
    """Calcula um dígito verificador do CPF (módulo 11; resto < 2 resulta em 0)."""
    total = sum(int(digit) * weight for digit, weight in zip(digits, range(first_weight, 1, -1)))
    remainder = total % 11
    return 0 if remainder < 2 else 11 - remainder


def is_valid_cpf(value: str) -> bool:
    """
    Valida os dois dígitos verificadores do CPF (pesos 10→2 e 11→2).
    Aceita valor com ou sem máscara. Rejeita os 11 dígitos iguais (ex.: 111.111.111-11).
    """
    digits = _only_digits(value)
    if len(digits) != CPF_LENGTH or len(set(digits)) == 1:
        return False
    first = _cpf_check_digit(digits[:9], first_weight=10)
    second = _cpf_check_digit(digits[:10], first_weight=11)
    return digits[9:] == f"{first}{second}"


def is_valid_cns(value: str) -> bool:
    """
    Valida o Cartão Nacional de Saúde: a soma de cada dígito multiplicado pelos pesos 15→1 deve ser
    divisível por 11. Vale para definitivos (1/2) e provisórios (7/8/9): a rotina oficial do DATASUS
    para os definitivos gera o número a partir do PIS de modo que essa mesma soma seja múltipla de 11,
    então a checagem é equivalente para validação (não para geração).
    """
    digits = _only_digits(value)
    if len(digits) != CNS_LENGTH or digits[0] not in "12789":
        return False
    total = sum(int(digit) * weight for digit, weight in zip(digits, range(CNS_LENGTH, 0, -1)))
    return total % CNS_DIVISOR == 0


def is_valid_luhn(value: str) -> bool:
    """Algoritmo de Luhn para números de cartão (13 a 19 dígitos)."""
    digits = _only_digits(value)
    if not LUHN_MIN_LENGTH <= len(digits) <= LUHN_MAX_LENGTH:
        return False
    total = 0
    for position, digit in enumerate(reversed(digits)):
        number = int(digit)
        if position % 2 == 1:
            number = number * 2 - 9 if number > 4 else number * 2
        total += number
    return total % 10 == 0


def is_valid_ip(candidate: str) -> bool:
    """Confirma um candidato de `IP_PATTERN` (IPv4 ou IPv6) com o módulo `ipaddress`."""
    try:
        ipaddress.ip_address(candidate)
    except ValueError:
        return False
    return True


def is_allowlisted_plate(match_text: str) -> bool:
    """True se o achado de placa começa por sigla clínica da `PLATE_ALLOWLIST` (ex.: TNM2017)."""
    return match_text[:3].upper() in PLATE_ALLOWLIST or match_text[:4].upper() in PLATE_ALLOWLIST


def matches_any_pii(text: str) -> bool:
    """True se o texto casa com qualquer padrão de `PII_PATTERNS` (não inclui o pseudônimo PAC)."""
    return any(pattern.search(text) for pattern in PII_PATTERNS.values())
