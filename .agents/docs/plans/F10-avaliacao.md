# F10 — Avaliação do Modelo e Análise de Resultados (E8)

> [Índice](INDEX.md) · Anterior: [← F9](F09-api-auth-interface.md) · Próxima: [F11 →](F11-documentacao-release.md)  
> Referências: [Contexto e decisões](00-contexto-e-decisoes.md) · [Modelo de execução](00-modelo-de-execucao.md)  
> **Status:** ⏳ Não iniciada

## Objetivo

Medir o ganho do fine-tuning e a qualidade, a segurança e a explicabilidade do assistente, com resultados reproduzíveis, tabelas e gráficos para o relatório; e calcular o **scorecard pré-registrado** de todos os candidatos, que fundamenta a escolha do modelo no painel admin.

## Ponto de partida
- **Projeto:** `training_scripts/utils/metrics_eval.py` (padrão de métricas em JSON); `genetic/hyperopt/visualizer.py` + `weights/genetic_experiments_results.json` (padrão de gráficos e tabela comparativa da Fase 2).
- **Fases anteriores:** `test.jsonl` congelado (F2); modelo base, adapter da config padrão e adapter vencedor da HPO (F3); `SEED_SCENARIOS` (F4); `redteam_prompts.jsonl` (F5); `rag_gold.jsonl` (F6); `AssistantService` (F7); `FlowService` (F8); registro de modelos (F3); `model_scorecard.yaml` congelado (F0); seção de modelos do painel admin (F9).

## Etapas e agentes
- **Etapas ativas:** 2 (desenho das métricas e da rubrica do juiz), 3 (harness com TDD), 4 (inclui a análise ética) e **checkpoint final**: o usuário escolhe o modelo ativo no painel admin com base nos scorecards.
- **Acionados:**

| Agente | Papel nesta fase |
| :--- | :--- |
| `ai-specialist` | Dono: métricas, LLM-as-judge, execução das avaliações, scorecard de todos os candidatos, análise dos resultados |
| `tester` | Testes do harness (métricas com valores conhecidos, determinismo por seed) |
| `developer` (×2) | Métricas + runner / juiz + relatório + scripts de execução + runner do scorecard |
| `ai-governance-auditor` | Viés, explicabilidade, enquadramento PL 2338/2023 e EU AI Act (alto risco) |
| `reviewer` | Quality Gate |

- **Não acionados:** `security` (o red-team foi criado e auditado na F5; aqui só é reexecutado), `privacy-officer` (a varredura de PII dos resultados é um teste automatizado), `dba`, `architect`, `designer`/`ux-reviewer`, `devops`.

## Execução em rodadas

| Rodada | Agente (paralelo) | Tarefas | Arquivos exclusivos |
| :--- | :--- | :--- | :--- |
| **R1** (Etapa 2) | `ai-specialist` | Métricas por dimensão (implementando exatamente as definições do `model_scorecard.yaml`, sem alterá-las), rubrica do juiz (correção, aderência ao protocolo, clareza, segurança, notas 1–5), `flow_scenarios.yaml` derivado de `SEED_SCENARIOS`, `internal_judge_set.jsonl` | `evaluation/datasets/{flow_scenarios.yaml, internal_judge_set.jsonl}`, `evaluation/harness/rubric.md` |
| **R2** (TDD) | `tester` | Métricas com entradas de resultado conhecido (predição perfeita → 1.0), runner com alvo fake, determinismo, varredura de PII nos resultados, cálculo do scorecard (normalização piso/meta, pesos, gates, desempate) contra o YAML congelado e conferência do hash | `tests/evaluation/*` |
| **R3** (código) | `developer#1` | 10.1, 10.2 | `evaluation/harness/{runner.py, metrics/*}` |
| | `developer#2` | 10.3, 10.4, 10.5, 10.8 | `evaluation/harness/{judge,report}.py`, `evaluation/run_all.py`, `finetuning/evaluate_model.py`, `evaluation/scorecard/{scorecard,run_scorecard}.py` |
| **R4** (execução) | `ai-specialist` | 10.6: baterias de modelo e de sistema **para cada candidato do registro** (bateria pesada no computador local, com a mesma imagem do `llama-server` e os mesmos GGUF; **só a latência**, 50 perguntas por candidato, medida no `healthai-llm` do Cloud Run (trocando o modelo ativo a cada finalista e restaurando o ativo no fim) para refletir produção, ≈ 50 min de uso; base e FT padrão na GPU local; Gemini no free tier) ∥ 10.8: scorecards gravados no registro | `evaluation/results/*` |
| **R5** (Etapa 4) | `ai-governance-auditor` ∥ `reviewer` ∥ `tester` | Parecer ético ∥ revisão ∥ suíte + Auto-Healer | `evaluation/results/governanca.md` |
| **R6** (Fechamento) | `ai-specialist` ∥ Orquestrador | 10.7: análise + seção E8 ∥ merge + `STATE.md` | `evaluation/results/summary.md`, `docs/fase3/secoes/07-avaliacao.md` |
| **Checkpoint** | Orquestrador → usuário (`ADMIN`) | Apresenta o ranking, os gates e a recomendação; **se nenhum fine-tuned for elegível, a fase volta para a F3** (P-051); senão, o usuário ativa um fine-tuned na seção **Modelo do Assistente** do painel admin | `ActiveModelStore` (gravado pelo painel) |

## Bateria

| Dimensão | Conjunto | Métrica | Comparação |
| :--- | :--- | :--- | :--- |
| Conhecimento biomédico | PubMedQA (test congelado) | Acurácia, F1-macro | Base vs FT |
| Ganho da otimização (D12) | PubMedQA + domínio interno (test) | Mesmas métricas acima | FT com config padrão vs FT com config vencedora da HPO |
| QA de saúde | MedQuAD (test) | ROUGE-L, BERTScore | Base vs FT |
| Domínio interno pt-BR | FAQ + protocolos (test) | LLM-as-judge (rubrica 1–5) + amostra revisada por humano | Base vs FT vs Gemini |
| Formato de documentos | Laudos/receitas (test) | Conformidade com o template e o aviso de validação | Base vs FT |
| RAG / Explainability | `rag_gold.jsonl` (parte de teste) | Precisão/recall de citação, recall@k, faithfulness | Configuração vencedora da ablação da F6 vs linha de base (MiniLM, só vetor, trechos de 1000 caracteres) |
| Segurança | `redteam_prompts.jsonl` | Bloqueio de injection, prescrição direta (meta 0%), recusa fora de escopo | Com vs sem guardrails |
| Fluxos | `flow_scenarios.yaml` | Precisão/recall de alertas, desfecho correto | — |
| Operacional | 50 perguntas fixas | Latência p50/p95 (fria e quente), tempo de carga e de troca de modelo, tokens, vCPU-s e custo de lista por resposta, projeção mensal contra o free tier | Fine-tuned (Cloud Run, CPU) vs Gemini |

> As métricas desta bateria que compõem o scorecard (D13) usam exatamente as definições, pisos, metas e pesos congelados em `model_scorecard.yaml` ([scorecard de modelos](00-scorecard-modelos.md)). As demais são análises complementares para o relatório.

## Código passo a passo
- [ ] **10.1 — `runner.py`:** `EvalRunner(target: Callable, dataset, metrics).run(seed) -> EvalResult`.
- [ ] **10.2 — `metrics/`:** `classification.accuracy_f1_macro`, `generation.rouge_l`/`bert_score`, `rag.citation_precision_recall`/`recall_at_k`/`faithfulness`, `safety.guardrail_rates`, `flows.alert_precision_recall`, `latency.percentiles` (funções puras).
- [ ] **10.3 — `judge.py`:** `LLMJudge(rubric, model)` → nota por critério + justificativa (o viés de usar Gemini como juiz fica documentado); roda no free tier do Gemini, com cache das notas e backoff; plano de cota: o juiz avalia só as respostas de nível sistema (finalistas e Gemini), em lotes diários se o limite do free tier exigir.
- [ ] **10.4 — `report.py`:** JSON + PNG (matplotlib, estilo do `visualizer.py`) + tabela markdown.
- [ ] **10.5 — `finetuning/evaluate_model.py` e `evaluation/run_all.py`:** CLIs com seed fixa.
- [ ] **10.6 — Execução** das duas baterias (no modelo: base, FT padrão e FT otimizado).
- [ ] **10.7 — `summary.md`:** onde o FT ajudou ou piorou (esquecimento em inglês, alucinação), custo, limitações e próximos passos.
- [ ] **10.8 — `evaluation/scorecard/`:** `scorecard.py` com `load_frozen_config(path, expected_sha256)` (falha se o hash divergir do ADR-009), `normalize(value, floor, target)`, `evaluate_gates(metrics, gates) -> dict[str, GateResult]` e `compute_scorecard(metrics, config) -> Scorecard`; `run_scorecard.py` (CLI) roda as baterias de modelo e de sistema para cada candidato do registro (sistema = `AssistantService` com o candidato forçado), grava o `scorecard` em `weights/llm/registry/<candidate_id>.json` (com `test_set_sha256` e `scorecard_config_sha256`) e exporta `evaluation/results/scorecard_ranking.{json,md,png}`.

## Critérios de aceite

Resultados reproduzíveis (exceto latência); tabela base vs FT; prescrição direta = 0% com guardrails; nenhum resultado com PII; parecer ético incluído; scorecard calculado para todos os candidatos com o YAML congelado (hash conferido); modelo ativo escolhido pelo usuário no painel; pelo menos um candidato fine-tuned elegível e ativado (P-051); custo do mês dentro da D14.

## Audit

(1) `run_all.py` 2× → métricas iguais; (2) métricas de sanidade; (3) varredura de PII em `results/`; (4) YAML do scorecard alterado → `run_scorecard` falha pelo hash; (5) candidato que viola um gate fica `eligible=false` e o painel bloqueia a ativação.

## Commits

`test(evaluation): adiciona cenarios de fluxo e conjunto do juiz` · `feat(evaluation): adiciona harness de metricas e llm-as-judge` · `feat(evaluation): avalia base vs fine-tuned e o sistema completo` · `docs(evaluation): consolida resultados e parecer etico` · `feat(evaluation): calcula scorecard pre-registrado dos candidatos`

## Entrega para a F11

Resultados, gráficos, `summary.md` e seção E8; registro com os scorecards e modelo ativo escolhido no painel.
