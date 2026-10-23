"""
Módulo Compartilhado de Governança de LLMs (Projetos 1 e 2).
Implementa:
1. PromptSecurityGuard: Sanitização restrita, truncamento anti-DDoS econômico,
   neutralização de delimitadores e bloqueio determinístico de Prompt Injection (PT/EN).
2. SimilarityLLMCache: Cache em memória de 2 níveis:
   - L1: Hash SHA-256 exato sobre texto normalizado (O(1)).
   - L2: Similaridade de Cosseno sobre N-gramas de caracteres + palavras (threshold >= 0.85)
     para reutilizar respostas em relatos clínicos ou perguntas logísticas similares.
"""

import hashlib
import math
import re
import time
import unicodedata
from collections import Counter
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class SecurityCheckResult:
    is_safe: bool
    sanitized_text: str
    wrapped_text: str
    blocked_reason: Optional[str] = None
    matched_pattern: Optional[str] = None


class PromptSecurityGuard:
    """
    Validador e sanitizador restrito contra Prompt Injection e Jailbreak (PT-BR e EN).
    """

    MAX_INPUT_CHARS: int = 2000

    INJECTION_PATTERNS: List[Tuple[str, str]] = [
        (r"ignore\s+(?:all\s+|previous\s+|prior\s+|above\s+|system\s+)*(?:instructions?|rules?|prompts?|directives?)", "EN_IGNORE_INSTRUCTIONS"),
        (r"disregard\s+(?:all\s+|previous\s+|prior\s+|above\s+|system\s+)*(?:instructions?|rules?|prompts?)", "EN_DISREGARD_INSTRUCTIONS"),
        (r"forget\s+(?:everything|all|your\s+instructions?|previous\s+instructions?|prior\s+rules?)", "EN_FORGET_INSTRUCTIONS"),
        (r"(?:reveal|show|print|output|repeat)\s+(?:your\s+|the\s+)?(?:system\s+prompt|instructions?|hidden\s+prompt|api\s+key|secret)", "EN_REVEAL_PROMPT"),
        (r"\b(?:jailbreak|dan\s+mode|developer\s+mode|do\s+anything\s+now|sudo\s+mode)\b", "EN_JAILBREAK_MODE"),
        (r"(?:you\s+are\s+now|act\s+as\s+if\s+you\s+are|pretend\s+(?:to\s+be|you\s+are))\s+(?:not\s+a\s+doctor|an?\s+unrestricted|evil|hacker|dan)", "EN_ROLE_HIJACK"),
        (r"\bsystem\s*prompt\b", "SYSTEM_PROMPT_PROBE"),
        (r"(?:ignore|ignorar|desconsidere)\s+(?:todas\s+as\s+|as\s+)?(?:instru[cç][oõ]es|regras|diretrizes|ordens)(?:\s+anteriores|\s+acima|\s+do\s+sistema)?", "PT_IGNORE_INSTRUCTIONS"),
        (r"(?:esque[cç]a|esquecer)\s+(?:tudo|todas\s+as\s+regras|as\s+instru[cç][oõ]es|regras\s+anteriores|que\s+voc[eê]\s+[eé])", "PT_FORGET_INSTRUCTIONS"),
        (r"(?:revele|mostre|exiba|imprima)\s+(?:suas\s+|as\s+|o\s+)?(?:instru[cç][oõ]es|prompt\s+de\s+sistema|regras\s+internas|chave\s+de\s+api)", "PT_REVEAL_PROMPT"),
        (r"(?:a\s+partir\s+de\s+agora\s+voc[eê]\s+[eé]|aja\s+como\s+se\s+n[aã]o\s+fosse|finja\s+ser\s+um)", "PT_ROLE_HIJACK"),
        (r"(?:me\s+passe\s+a\s+receita\s+de\s+uma\s+bomba|como\s+fazer\s+uma\s+bomba|bypass\s+safety)", "MALICIOUS_PAYLOAD"),
    ]

    @classmethod
    def sanitize_delimiters(cls, text: str, max_chars: Optional[int] = None) -> str:
        """
        Trunca no limite seguro de caracteres e neutraliza delimitadores Markdown/XML
        que poderiam escapar do bloco de isolamento de dados do usuário.
        """
        if not text:
            return ""
        limit = max_chars or cls.MAX_INPUT_CHARS
        cleaned = str(text)[:limit]
        cleaned = cleaned.replace("```", "'''")
        cleaned = re.sub(
            r"</?\s*(?:untrusted_user_input|system|instruction|prompt|context)\s*>",
            "[TAG_REMOVED]",
            cleaned,
            flags=re.IGNORECASE,
        )
        return cleaned.strip()

    @classmethod
    def inspect(cls, text: str, max_chars: Optional[int] = None) -> SecurityCheckResult:
        """
        Inspeciona o input do usuário, detecta padrões de Prompt Injection e retorna
        o texto sanitizado e encapsulado em tags XML de isolamento.
        """
        sanitized = cls.sanitize_delimiters(text, max_chars=max_chars)
        if not sanitized:
            return SecurityCheckResult(
                is_safe=True,
                sanitized_text="",
                wrapped_text="<untrusted_user_input></untrusted_user_input>",
            )

        for pattern, label in cls.INJECTION_PATTERNS:
            if re.search(pattern, sanitized, flags=re.IGNORECASE):
                return SecurityCheckResult(
                    is_safe=False,
                    sanitized_text="[BLOCKED_PROMPT_INJECTION]",
                    wrapped_text="<untrusted_user_input>[BLOCKED_PROMPT_INJECTION]</untrusted_user_input>",
                    blocked_reason=f"Prompt injection pattern detected ({label})",
                    matched_pattern=label,
                )

        wrapped = f"<untrusted_user_input>\n{sanitized}\n</untrusted_user_input>"
        return SecurityCheckResult(
            is_safe=True,
            sanitized_text=sanitized,
            wrapped_text=wrapped,
        )


class SimilarityLLMCache:
    """
    Cache em duas camadas para respostas de LLMs (FinOps & Baixa Latência):
    - L1: Hash SHA-256 exato sobre o texto normalizado (O(1)).
    - L2: Similaridade de Cosseno sobre N-gramas de caracteres (3-gramas) e tokens
      de palavras (threshold configurável, padrão >= 0.85).
    """

    def __init__(
        self,
        similarity_threshold: float = 0.85,
        ttl_seconds: int = 86400,
        max_entries: int = 512,
    ):
        self.similarity_threshold = similarity_threshold
        self.ttl_seconds = ttl_seconds
        self.max_entries = max_entries
        self._l1_exact: Dict[str, Tuple[Any, float]] = {}
        self._l2_entries: List[Dict[str, Any]] = []
        self.stats = {"l1_hits": 0, "l2_hits": 0, "misses": 0}

    @staticmethod
    def normalize_text(text: str) -> str:
        """
        Normaliza texto: lowercase, sem acentos, sem pontuação e espaços colapsados.
        """
        if not text:
            return ""
        lowered = str(text).lower().strip()
        decomposed = unicodedata.normalize("NFKD", lowered)
        without_accents = "".join(ch for ch in decomposed if not unicodedata.combining(ch))
        alnum_only = re.sub(r"[^a-z0-9\s]", " ", without_accents)
        return re.sub(r"\s+", " ", alnum_only).strip()

    @classmethod
    def _build_feature_counter(cls, normalized_text: str) -> Counter:
        """
        Gera vetor esparso combinando tokens de palavras (peso 1.5) e 3-gramas de caracteres (peso 1.0).
        Permite capturar alta similaridade mesmo com pequenas variações de digitação ou sinônimos próximos.
        """
        features: Counter = Counter()
        if not normalized_text:
            return features

        tokens = normalized_text.split()
        for tok in tokens:
            if len(tok) >= 2:
                features[f"w:{tok}"] += 1.5

        compact = f" {normalized_text} "
        for i in range(max(0, len(compact) - 2)):
            trigram = compact[i : i + 3]
            features[f"c:{trigram}"] += 1.0

        return features

    @staticmethod
    def cosine_similarity(vec_a: Counter, vec_b: Counter) -> float:
        if not vec_a or not vec_b:
            return 0.0
        intersection = set(vec_a.keys()) & set(vec_b.keys())
        dot_product = sum(vec_a[k] * vec_b[k] for k in intersection)
        if dot_product <= 0.0:
            return 0.0
        norm_a = math.sqrt(sum(v * v for v in vec_a.values()))
        norm_b = math.sqrt(sum(v * v for v in vec_b.values()))
        if norm_a == 0.0 or norm_b == 0.0:
            return 0.0
        return dot_product / (norm_a * norm_b)

    def _make_l1_key(self, namespace: str, normalized_text: str) -> str:
        raw = f"{namespace}::{normalized_text}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def _prune_expired(self, now: float) -> None:
        expired_keys = [
            k for k, (_, ts) in self._l1_exact.items() if now - ts >= self.ttl_seconds
        ]
        for k in expired_keys:
            self._l1_exact.pop(k, None)
        self._l2_entries = [
            entry for entry in self._l2_entries if now - entry["timestamp"] < self.ttl_seconds
        ]

    def get(
        self,
        text: str,
        namespace: str = "default",
        threshold: Optional[float] = None,
    ) -> Optional[Any]:
        """
        Busca no cache L1 (hash exato normalizado) e, se não encontrar,
        busca no cache L2 por similaridade de cosseno >= threshold.
        """
        normalized = self.normalize_text(text)
        if not normalized:
            return None

        now = time.time()
        self._prune_expired(now)

        # 1. Camada L1: Exact Normalized SHA-256
        l1_key = self._make_l1_key(namespace, normalized)
        if l1_key in self._l1_exact:
            val, _ = self._l1_exact[l1_key]
            self.stats["l1_hits"] += 1
            return val

        # 2. Camada L2: Similaridade de Cosseno no mesmo namespace
        min_sim = threshold if threshold is not None else self.similarity_threshold
        query_vec = self._build_feature_counter(normalized)
        best_score = 0.0
        best_val: Optional[Any] = None

        for entry in self._l2_entries:
            if entry["namespace"] != namespace:
                continue
            sim = self.cosine_similarity(query_vec, entry["vector"])
            if sim >= min_sim and sim > best_score:
                best_score = sim
                best_val = entry["value"]

        if best_val is not None:
            self.stats["l2_hits"] += 1
            return best_val

        self.stats["misses"] += 1
        return None

    def set(self, text: str, value: Any, namespace: str = "default") -> None:
        """
        Armazena a resposta simultaneamente nas camadas L1 (SHA-256) e L2 (Vetor N-gram).
        """
        normalized = self.normalize_text(text)
        if not normalized:
            return

        now = time.time()
        self._prune_expired(now)

        if len(self._l2_entries) >= self.max_entries:
            self._l2_entries.pop(0)

        l1_key = self._make_l1_key(namespace, normalized)
        self._l1_exact[l1_key] = (value, now)

        vec = self._build_feature_counter(normalized)
        for entry in self._l2_entries:
            if entry["namespace"] == namespace and entry["normalized"] == normalized:
                entry["value"] = value
                entry["timestamp"] = now
                entry["vector"] = vec
                return

        self._l2_entries.append(
            {
                "namespace": namespace,
                "normalized": normalized,
                "vector": vec,
                "value": value,
                "timestamp": now,
            }
        )

    def clear(self) -> None:
        self._l1_exact.clear()
        self._l2_entries.clear()
        self.stats = {"l1_hits": 0, "l2_hits": 0, "misses": 0}


# Instância global compartilhada pelos serviços de LLM
shared_llm_cache = SimilarityLLMCache(similarity_threshold=0.85, ttl_seconds=86400)
