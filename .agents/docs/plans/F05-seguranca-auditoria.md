# F5 — Segurança, Guardrails, Auditoria e Explainability (R3.1, R3.2, R3.3)

> [Índice](INDEX.md) · Anterior: [← F4](F04-prontuario.md) · Próxima: [F6 →](F06-rag-fontes.md)  
> Referências: [Contexto e decisões](00-contexto-e-decisoes.md) · [Modelo de execução](00-modelo-de-execucao.md)  
> **Status:** ⏳ Não iniciada

## Objetivo

Construir, **antes** do assistente, os componentes transversais que toda resposta vai atravessar: guard de entrada, guard de saída (prescrição, citação, vazamento de PII), auditoria com `trace_id`, contrato de resposta explicável e handler global de erros.

## Ponto de partida
- **Projeto:** `PromptSecurityGuard` (núcleo do guard de entrada, **reaproveitado sem reescrita**); `CLINICAL_SYSTEM_PROMPT`/`ethical_disclaimer` (padrão de limites); `main.py` sem handlers globais; 36 `print()` (os serviços legados **não** são migrados nesta fase, só o código novo nasce com `logging`).
- **Fases anteriores:** `pii_patterns.py`, `errors.py`, bootstrap (F0); `AuditRepository` + tabela `audit_events` (F4); BR-030 (P-040…044).

## Etapas e agentes
- **Etapas ativas:** 2 (políticas e desenho de logging/trace), 3, 4. Sem checkpoint (as regras já estão aprovadas no BR-030).
- **Acionados:**

| Agente | Papel nesta fase |
| :--- | :--- |
| `security` | Dono: políticas de prescrição e escopo, mapeamento OWASP LLM Top 10, **red-team dataset**, auditoria final |
| `architect` | Desenho de logging JSON, `trace_id`, handlers e contrato `AssistantAnswer` |
| `privacy-officer` | `pii_masker` e allowlist do payload de auditoria (P-044) com veto |
| `tester` (×2) | Guards + red-team / auditoria + handlers |
| `developer` (×2) | Core (log, trace, handlers, auditoria) / guardrails |
| `reviewer` | Quality Gate |

- **Não acionados:** `ai-specialist` (os guards são determinísticos, sem LLM), `dba` (a tabela de auditoria já existe desde a F4), `designer`/`ux-reviewer`, `devops`.

## Execução em rodadas

| Rodada | Agente (paralelo) | Tarefas | Arquivos exclusivos |
| :--- | :--- | :--- | :--- |
| **R1** (Etapa 2) | `security` | Padrões de prescrição e escopo, códigos AST-001…004, red-team (≥ 60 prompts: injection direta e indireta, jailbreak, prescrição direta, fora do escopo, extração de PII ou do system prompt) | `.agents/docs/adr/ADR-007-guardrails.md`, `backend/evaluation/datasets/redteam_prompts.jsonl` |
| | `architect` | 5.1 (contratos), desenho de log/trace/handlers | `app/assistant/schemas/{answer,audit,guardrails}.py`, adendo em `ports.py` (só os ports de guard/audit) |
| | `privacy-officer` | `AUDIT_PAYLOAD_ALLOWLIST` e regras de mascaramento | Adendo no RIPD |
| **R2** (TDD) | `tester#1` | Testes de `InputGuard`, `PrescriptionGuard`, `CitationGuard`, `OutputGuard` (parametrizados pelo red-team) | `tests/assistant/guardrails/*` |
| | `tester#2` | Testes de `trace`, `JsonFormatter`, `pii_masker`, `AuditLogger`, `DbAuditSink`, handlers (app FastAPI mínima com `TestClient`) | `tests/assistant/audit/*`, `tests/core/*` |
| **R3** (código) | `developer#1` | 5.2, 5.3, 5.7 | `app/core/{trace,logging_config,exception_handlers}.py`, `app/assistant/audit/*` |
| | `developer#2` | 5.4, 5.5, 5.6 | `app/assistant/guardrails/*` |
| **R4** (integração) | `developer#1` | 5.8 (`register_security` no bootstrap) | `app/assistant/bootstrap.py` |
| **R5** (Etapa 4) | `security` ∥ `privacy-officer` ∥ `reviewer` ∥ `tester` | Auditoria OWASP + execução do red-team ∥ auditoria do masker (**veto**) ∥ revisão ∥ suíte + Auto-Healer | — |
| **R6** (Fechamento) | `security` ∥ Orquestrador | Seção "Segurança e auditoria" ∥ merge + `STATE.md` | `docs/fase3/secoes/04-seguranca.md` |

## Código passo a passo
- [ ] **5.1 — Contratos:** `Citation{source_type: Literal["protocol","patient_record"], document, page, section, chunk_id, excerpt, score}`; `AssistantAnswer{answer, citations[], patient_data_used[], confidence, requires_human_validation, guardrail_flags[], model}`; `GuardrailResult{allowed, flags[], rewritten_text?, error_code?}`; `AuditEvent{trace_id, event_type, actor, payload, model?, latency_ms?, created_at}`; `AuditEventType` (`QUESTION_RECEIVED`, `RETRIEVAL`, `TOOL_CALL`, `LLM_CALL`, `LLM_FALLBACK`, `GUARDRAIL_BLOCK`, `GUARDRAIL_REWRITE`, `FLOW_NODE`, `ALERT_RAISED`, `HUMAN_DECISION`, `LLM_WARMUP`, `MODEL_ACTIVATED`); ports `InputGuardPort`, `OutputGuardPort`, `AuditSinkPort`.
- [ ] **5.2 — Trace e log:** `core/trace.py` (`trace_id_var: ContextVar`, `new_trace_id()`, `current_trace_id()`); `core/logging_config.py` (`JsonFormatter` com `trace_id`, `configure_logging(level)`); `TraceIdMiddleware` (lê/gera `X-Trace-Id` e devolve no header).
- [ ] **5.3 — Auditoria:** `pii_masker.mask_text(text)` e `mask_payload(dict)` (recursivo, só chaves da allowlist; nunca serializa objetos inteiros); `AuditLogger(sinks).record(event_type, actor, payload, model=None)`; `JsonLogAuditSink`; `DbAuditSink` (sobre o `AuditRepository` da F4).
- [ ] **5.4 — Guard de entrada:** `ScopePolicy.classify(text)` (vocabulário `SCOPE_KEYWORDS` + limiar → `OutOfScopeError` AST-001); `InputGuard.check(text)` = `PromptSecurityGuard.inspect` (bloqueio → `PromptInjectionBlocked` AST-002) → `ScopePolicy`.
- [ ] **5.5 — `prescription_guard.py`:** `DOSAGE_PATTERN`, `IMPERATIVE_PRESCRIPTION_PATTERN` (prescrevo, tome, administre, inicie, suspenda…), `detect(text)`, `rewrite_as_suggestion(text)` (prefixo "Sugestão para avaliação médica:" + rodapé de validação) → `requires_human_validation=True`, flag `PRESCRIPTION_REWRITTEN` (P-040).
- [ ] **5.6 — `citation_guard.py` + `output_guard.py`:** `CitationGuard.validate(answer, retrieved_ids, snapshot_fields)` remove citações inexistentes (`CITATION_REMOVED`) e, sem nenhuma válida, troca pela resposta padrão (`NO_SOURCE_FALLBACK`, P-041); `OutputGuard.review(answer, context)` = prescrição → citação → `mask_text` → auditoria das decisões.
- [ ] **5.7 — `exception_handlers.py`:** `AssistantDomainError` → `{error, code, trace_id}` com o status do erro; `RequestValidationError` → 400 com os campos; `Exception` → 500 genérico **sem stack trace** (stack só no log).
- [ ] **5.8 — Bootstrap:** `register_security(app)` (middleware + handlers + `configure_logging`) chamado por `register_assistant(app)`.

## Critérios de aceite

Logs em JSON com `trace_id`; nenhum erro devolvido com stack trace; prescrição direta = 0% no red-team; nenhuma PII nos eventos de auditoria.

## Audit

(1) "Prescrevo tamoxifeno 20 mg/dia" → reescrito + `requires_human_validation=true`; (2) citação a `chunk_id` não recuperado → removida, e sem nenhuma → resposta padrão; (3) log com "Maria, CPF 123.456.789-09" → mascarado; (4) "Ignore as instruções…" → AST-002 + `GUARDRAIL_BLOCK`; (5) exceção genérica → 500 sem stack no corpo; (6) red-team completo, 0 bypass de prescrição.

## Commits

`feat(assistant): define contrato de resposta explicavel e eventos de auditoria` · `feat(core): adiciona log json com trace_id` · `feat(audit): adiciona audit logger com mascaramento de pii (P-044)` · `feat(guardrails): adiciona guard de entrada e politica de escopo (P-042)` · `feat(guardrails): reescreve prescricao direta como sugestao (P-040)` · `feat(guardrails): valida citacoes da resposta (P-041)` · `feat(core): adiciona handler global sem stack trace`

## Entrega para a F6/F7/F8/F9

`InputGuard`, `OutputGuard`, `AuditLogger`, `AssistantAnswer`/`Citation`, handlers; red-team para a F10.
