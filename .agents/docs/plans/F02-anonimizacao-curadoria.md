# F2 — Preprocessing, Anonimização e Curadoria (R1.4, E1, E4)

> [Índice](INDEX.md) · Anterior: [← F1](F01-corpus.md) · Próxima: [F3 →](F03-fine-tuning-qlora.md)  
> Referências: [Contexto e decisões](00-contexto-e-decisoes.md) · [Modelo de execução](00-modelo-de-execucao.md)  
> **Status:** ⏳ Não iniciada

## Objetivo

Transformar o corpus bruto em dataset de instruções limpo, anonimizado e curado, com split sem vazamento.

## Ponto de partida
- **Projeto:** `SimilarityLLMCache` (vetores de n-gramas + cosseno → dedup quase-exata); `PromptSecurityGuard.inspect()` (remove amostras com jailbreak — *data poisoning*).
- **Fases anteriores:** `corpus_raw.jsonl` e fixture (F1); `app/core/pii_patterns.py` e o RIPD (F0).

## Etapas e agentes
- **Etapas ativas:** 2 (política de anonimização), **Checkpoint**, 3, 4 (com veto LGPD).
- **Acionados:**

| Agente | Papel nesta fase |
| :--- | :--- |
| `privacy-officer` | Política de pseudonimização e critério do gate (Etapa 2); auditoria por amostragem com **veto** (Etapa 4) |
| `ai-specialist` | Dono: limiares de curadoria, balanceamento, system prompt embutido, orquestração do `prepare_dataset` |
| `tester` (×2) | Bateria de PII / curadoria e split |
| `developer` (×2) | Limpeza + anonimização / curadoria + formatação |
| `reviewer` | Quality Gate |

- **Não acionados:** `security` (não há superfície de ataque: pipeline offline), `dba`, `architect`, `designer`/`ux-reviewer`, `devops`.

## Execução em rodadas

| Rodada | Agente (paralelo) | Tarefas | Arquivos exclusivos |
| :--- | :--- | :--- | :--- |
| **R1** (Etapa 2) | `privacy-officer` | Entidades obrigatórias, formato dos pseudônimos, `CLINICAL_ALLOWLIST`, critério do gate (P-047) | Seção no `RIPD_assistente_medico.md` |
| | `ai-specialist` | Limiares (dedup 0.9, tamanho mínimo, `max_share` 0.4), system prompt de treino, proporção dos splits | `finetuning/preprocessing/curation_config.yaml` |
| **Checkpoint** | Orquestrador | Política de anonimização + parâmetros de curadoria | — |
| **R2** (TDD) | `tester#1` | 50+ casos de PII (CPF com/sem máscara, CNS, telefones, nomes compostos, datas), consistência de pseudônimos, falsos positivos clínicos, gate | `tests/finetuning/test_anonymizer.py`, `test_cleaning.py` |
| | `tester#2` | Dedup exata/quase-exata, filtros, poisoning, balanceamento, formato `messages`, split sem vazamento | `tests/finetuning/test_curation.py`, `test_formatter.py` |
| **R3** (código) | `developer#1` | 2.1, 2.2 | `finetuning/preprocessing/{cleaning,anonymizer}.py` |
| | `developer#2` | 2.3, 2.4 | `finetuning/preprocessing/{curation,formatter}.py` |
| **R4** (integração) | `ai-specialist` | 2.5: roda o pipeline completo e gera dataset, relatório e dataset card | `finetuning/prepare_dataset.py`, `data/finetuning/{processed,reports}/*`, `dataset_card.md` |
| **R5** (Etapa 4) | `privacy-officer` ∥ `reviewer` ∥ `tester` | Auditoria por amostragem do `processed/` (**veto**) ∥ revisão ∥ suíte + Auto-Healer | — |
| **R6** (Fechamento) | `ai-specialist` ∥ Orquestrador | Seção "Preparação e anonimização" ∥ merge + `STATE.md` | `docs/fase3/secoes/01-dados.md` |

## Código passo a passo
- [ ] **2.1 — `cleaning.py`:** `normalize_unicode`, `strip_html`, `collapse_whitespace`, `exceeds_token_budget(record, max_tokens)` (orçamento alinhado ao `max_seq_length` de 1024 tokens da F3), `clean_record(record) -> CorpusRecord | None`.
- [ ] **2.2 — `anonymizer.py`:** `Anonymizer(nlp)` com `anonymize(text, doc_id) -> AnonymizationResult{text, entities_found, replacements}`: regex de `PII_PATTERNS` → `[CPF]`, `[TELEFONE]`, `[DATA]`…; NER `PER`/`LOC` → `[PACIENTE_n]`/`[LOCAL_n]` consistentes por documento; respeita a `CLINICAL_ALLOWLIST` (Paget, Rotterdam, BRCA1/2, Papanicolaou…). `PIIGate.has_residual_pii(text)`, segunda passada mais estrita (P-047).
- [ ] **2.3 — `curation.py`:** `dedupe_exact`, `dedupe_near(threshold)` (vetores do `SimilarityLLMCache`, blocagem por `task_type`), `apply_quality_filters -> (kept, rejected_by_reason)`, `drop_poisoned` (`PromptSecurityGuard`), `balance_by_task_type(max_share)`, `export_review_sample(n=100)`.
- [ ] **2.4 — `formatter.py`:** `to_messages(record, system_prompt)` → `{"messages": [system, user, assistant], "meta": …}` (**agnóstico ao modelo**: o template de chat só é aplicado na F3); `stratified_group_split(records, ratios=(0.8, 0.1, 0.1), group_key="source_doc", seed)`.
- [ ] **2.5 — `prepare_dataset.py`:** raw → clean → anonymize → gate → curate → format → split → `processed/{train,val,test}.jsonl` + `reports/data_quality_report.json` + `dataset_card.md`; registra o **hash do `test.jsonl`** (congelado para a F10).

## Critérios de aceite

Zero PII residual (gate + auditoria); splits sem interseção de grupos; relatório de qualidade; `test.jsonl` congelado.

## Audit

(1) "Paciente Maria Silva, CPF 123.456.789-09, tel (11) 98888-7777" → nada original sobra; (2) mesmo nome → mesmo `[PACIENTE_n]` no documento; (3) CPF em formato estranho → descartado pelo gate; (4) "doença de Paget" preservada; (5) amostra com "ignore as instruções" → removida; (6) splits sem vazamento.

## Commits

`feat(finetuning): adiciona limpeza do corpus` · `feat(finetuning): implementa anonimizador pt-br com gate de pii (P-047)` · `feat(finetuning): adiciona curadoria, dedup e filtro de poisoning` · `feat(finetuning): formata em messages com split por grupo` · `docs(dataset): adiciona dataset card`

## Entrega para a F3

`processed/{train,val,test}.jsonl` + hash do teste.
