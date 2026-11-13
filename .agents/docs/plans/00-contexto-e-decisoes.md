# Fase 3 — Contexto, Requisitos e Decisões

> [Índice do plano](INDEX.md) · [Modelo de execução](00-modelo-de-execucao.md)

## 0. Resumo do Desafio (PDF)

O hospital quer um **assistente virtual médico treinado com dados próprios**, capaz de:
- auxiliar nas condutas clínicas, responder dúvidas de médicos e sugerir procedimentos com base nos protocolos internos;
- executar **fluxos de decisão automatizados e seguros** (ex.: ao receber um paciente → verificar exames pendentes → sugerir tratamentos → emitir alertas à equipe), coordenados com **LangChain**.

### Requisitos obrigatórios

| ID | Requisito do PDF |
| :--- | :--- |
| **R1.1** | Fine-tuning de uma LLM (LLaMA, Falcon ou outra) com protocolos médicos do hospital |
| **R1.2** | … com exemplos de perguntas frequentes feitas por médicos |
| **R1.3** | … com modelos de laudos, receitas e procedimentos internos |
| **R1.4** | Preparar os dados com preprocessing, anonimização e curadoria |
| **R2.1** | LangChain: pipeline que integra a LLM customizada |
| **R2.2** | LangChain: consultas em base de dados estruturada (prontuários e registros) |
| **R2.3** | LangChain: contextualizar respostas com informações atualizadas do paciente |
| **R3.1** | Limites de atuação (ex.: nunca prescrever diretamente sem validação humana) |
| **R3.2** | Logging detalhado para rastreamento e auditoria |
| **R3.3** | Explainability (indicar a fonte da informação usada na resposta) |
| **R4.1** | Projeto modularizado em Python |
| **R4.2** | Instruções completas no README |

### Entregáveis

| ID | Entregável do PDF |
| :--- | :--- |
| **E1** | Repositório com pipeline de fine-tuning |
| **E2** | Repositório com integração LangChain |
| **E3** | Repositório com fluxos LangGraph |
| **E4** | Dataset anonimizado ou dados sintéticos de exemplo |
| **E5** | Relatório técnico: processo de fine-tuning |
| **E6** | Relatório técnico: descrição do assistente médico |
| **E7** | Relatório técnico: diagrama do fluxo LangChain |
| **E8** | Relatório técnico: avaliação do modelo e análise de resultados |
| **E9** | Vídeo de até 15 min: treino e funcionamento da LLM, execução de um fluxo automatizado, perguntas clínicas contextualizadas, logs e validação das respostas |

---

## 1. Ponto de Partida do Projeto (Inventário Reaproveitável)

### 1.1 Ativos existentes e onde cada um é reaproveitado

| Ativo existente | Arquivo / símbolo | Como a Fase 3 usa | Fase |
| :--- | :--- | :--- | :--- |
| Guard anti prompt injection (PT/EN) | `backend/app/services/llm_governance.py` → `PromptSecurityGuard.inspect()`, `sanitize_delimiters()`, `INJECTION_PATTERNS` | Núcleo do `InputGuard`; filtro anti *data poisoning* no dataset; sanitização do contexto do RAG | F2, F5, F6 |
| Cache L1/L2 por similaridade | `llm_governance.py` → `SimilarityLLMCache` (`normalize_text`, `_build_feature_counter`, `cosine_similarity`), `shared_llm_cache` | Deduplicação quase-exata do dataset; cache de respostas sem paciente | F2, F7 |
| Cadeia de fallback de LLM | `services/clinical_llm.py` → `ClinicalLLMService` (Gemini → Gemini → OpenAI → heurística); `services/logistics_llm.py` → `_invoke_llm_with_fallback()` | Referência do `llm/provider.py` (fine-tuned via `llama-server` → Gemini só como contingência). A OpenAI fica fora do assistente (sem crédito disponível); o código legado que a usa não muda | F7 |
| Padrão "apoio à decisão + disclaimer" | `clinical_llm.py` → `CLINICAL_SYSTEM_PROMPT`, `ClinicalReportSchema.ethical_disclaimer` | Base do system prompt do assistente e da regra P-040 | F5, F7 |
| RAG LangChain + Chroma | `knowledge_base/ingest_docs.py` (`PyPDFLoader` já grava `source`/`page`); `query_rag.py` → `get_rag_context()` (usado por `app/ml/text.py::TextPredictor._fetch_rag_context`) e `query_rag()` | Migração para pgvector no Supabase com a estratégia de vetorização (D17); `get_rag_context` reimplementado **mantendo a assinatura** (Fase 1 intacta); o Chroma sai | F6 |
| 5 PDFs de diretrizes | `backend/knowledge_base/docs/*.pdf` | Fazem o papel dos "protocolos internos"; fonte do QA sintético | F1, F6 |
| Laboratório offline de treino | `backend/training_scripts/` (`train_all.py`, `train_genetic_hyperopt.py`, `utils/metrics_eval.py`) | Padrão de pasta, CLI e métricas (JSON + PNG) para `backend/finetuning/` | F1–F3 |
| Padrão de gráficos de experimentos | `app/genetic/hyperopt/visualizer.py`, `weights/genetic_experiments_results.json` | Estilo de plots e tabela comparativa | F3, F10 |
| SQLite local | `services/geo/geo_cache.py` (`sqlite3` puro, arquivo em `app/data/`) | Não muda; a base nova vai para o Supabase (D15) | F4 |
| Auth JWT do admin | `api/routers/admin.py` → `create_access_token()`, `get_current_admin()`, `OAuth2PasswordBearer`, `/admin/login` | Evolui para `app/core/security.py` com papéis `ADMIN`/`MEDICO` e cookie HttpOnly | F9 |
| Seleção de modelos ativos no admin | `admin.py` → `GET/POST /admin/active-models` (`weights/active_models.json`, chaves `pcos`, `cancer`, `vision_cancer`, `llm`); `InferenceService._get_active_model()` lê o JSON a cada análise; `admin-dashboard` com cards de modelo, métricas e `setAsActive()` | Mesmo mecanismo para o modelo do assistente: chave nova `assistant_llm`, provider lendo a escolha a cada requisição e seção nova no `admin-dashboard` com o scorecard | F7, F9 |
| CORS com credenciais | `main.py` → `CORSMiddleware(allow_credentials=True, origens explícitas)` | Fica só para os endpoints públicos legados chamados direto no `run.app`; as rotas autenticadas passam pelo Firebase Hosting, na mesma origem (D16) | F9 |
| Rate limiter global | `main.py` → `AdvancedExponentialRateLimiter` (30 req/min) | Mantido; o assistente ganha um limite próprio no router | F9 |
| Lifespan | `main.py` → `lifespan()` → `inference_service.load_all_models()` | Ganha `init_assistant_resources()` (hook único criado na F0) | F0 |
| Frontend Angular 21 | `app.routes.ts`, `app.html` (nav), `auth.service.ts` (JWT em `localStorage`), `auth.interceptor.ts` (Bearer), `auth.guard.ts`, `components/{button,card,input}` | Rota `/assistant`; auth migrada para cookie; componentes reaproveitados | F9 |
| Chat de rotas | `routes_router.py` → `POST /api/v1/routes/chat`; `routes.service.ts`; página `medical-routes` | Referência de UX e código para o chat do assistente | F9 |
| Design System | `.agents/docs/design/DESIGN_SYSTEM.md`, `design/specimen/prontuario-kit.html` | Tokens e padrões da tela do assistente | F9 |
| Testes pytest | `backend/tests/` (27 testes, sem `conftest.py`/`pytest.ini`) | Ganham infraestrutura comum na F0 | F0 |
| CI/CD | `.github/workflows/deploy.yml` (deploy em push na `master`, **sem testes**) | Job de testes na F0; envs novas na F11 | F0, F11 |
| Relatórios anteriores | `docs/fase2/relatorio-tecnico-fase2.md`, `docs/fase2/roteiro-video-apresentacao.md`, `docs_en/` | Estrutura do relatório e do roteiro da Fase 3 | F11 |

### 1.2 Lacunas que a Fase 3 resolve

| # | Lacuna | Fase |
| :--- | :--- | :--- |
| L1 | Não há pipeline de fine-tuning nem dataset de instruções | F1–F3 |
| L2 | Não há base estruturada de prontuários/registros | F4 |
| L3 | Logging com `print()` (36 ocorrências em `app/`), sem `trace_id` nem auditoria | F5 |
| L4 | `query_rag.py` descarta os metadados (`"\n\n".join(doc.page_content …)`) e recria o embedding a cada chamada | F6 |
| L5 | Não há LangGraph | F8 |
| L6 | `requirements.txt` sem `langchain-google-genai`, `langchain-huggingface`, `langchain-text-splitters` (já importados) e sem `langgraph` | F0 |
| L7 | JWT em `localStorage` (`auth.service.ts:36`) — viola a regra "JWT só em Cookie HttpOnly" | F9 |
| L8 | Não há perfil `MEDICO` nem identidade do aprovador | F9 |
| L9 | Sem `conftest.py`/markers → testes de LLM dependeriam de rede | F0 |
| L10 | Deploy automático na `master` sem testes | F0 |
| L11 | Routers atuais sem envelope `data`/`meta`. **Fora do escopo:** os routers novos já nascem com envelope; o legado fica registrado como dívida técnica | F9 |
| L12 | `Dockerfile` copia `training_scripts/` e `knowledge_base/` inteiros → excluir `finetuning/`, `data/finetuning/`, `evaluation/` | F0 |
| L13 | `GET /admin/active-models` não exige autenticação (só o `POST` exige). **Fora do escopo** do legado; os endpoints novos de modelos do assistente nascem protegidos (`ADMIN`) | F9 |

---

## 2. Decisões de Arquitetura Propostas

> [!IMPORTANT]
> As decisões ❓ aguardam o usuário. Pela ordem sequencial, **precisam estar tomadas antes da F3** (F0–F2 não dependem delas: o dataset da F2 sai no formato `messages`, agnóstico ao modelo).

| ID | Decisão | Recomendação | Alternativa |
| :--- | :--- | :--- | :--- |
| **D1** ❓ | Modelos candidatos | **Triagem de 5 modelos base** pequenos o bastante para treinar nos 6 GB e servir em CPU: `Llama-3.2-1B-Instruct` (família LLaMA citada no PDF), `Qwen2.5-1.5B-Instruct`, `Qwen3-1.7B`, `Gemma-3-1B-it` e `Tucano-2b4-Instruct` (nativo em português). Os **2–3 finalistas**, por regra pré-registrada, passam pela HPO e viram candidatos selecionáveis; o Gemini fica como referência (D13). A escolha final é feita no painel admin. Lista conferida na F0 contra modelos mais novos | Modelos de 3B ou mais (lentos em CPU; inviáveis no orçamento da D14); treinar todos com HPO completa (tempo de GPU) |
| **D2** | Técnica | QLoRA (4-bit NF4 + LoRA) com `transformers` + `peft` + `trl` | Full fine-tuning (inviável sem A100) |
| **D3** | Onde treinar | **No computador pessoal (GTX 1660 SUPER 6 GB, i5-11400, 32 GB RAM, WSL2 Ubuntu)**, com QLoRA 4-bit e Unsloth (se compatível), candidatos em sequência e busca retomável. Kaggle gratuito como contingência ou para paralelizar o segundo candidato | Kaggle/Colab gratuitos como ambiente principal; HF Jobs ou VM GPU (pagos; fora da D14) |
| **D4** ❓ | Como servir em produção | **Obrigatório: o fine-tuned responde em produção.** Serviço único `healthai-llm` no Cloud Run com `llama-swap` + `llama-server` (llama.cpp, CPU, 4 vCPU / 4 GiB): só o modelo ativo fica em memória, e os outros finalistas ficam no Cloud Storage e são carregados sob demanda na troca. Escala a zero, `max-instances 1`, acesso privado (IAM + ID token), dentro do free tier. O modelo ativo é carregado automaticamente junto com o cold start do sistema (P-052). Gemini só como contingência, sem dados de paciente (P-051). O ❓ é confirmar a latência medida na F3 | Um serviço por candidato (mais deploys e IAM); GPU no Cloud Run, Vertex AI ou HF Inference Endpoints (custo por hora; fora da D14) |
| **D5** | Base de prontuários | **Postgres do Supabase (free tier)** + SQLAlchemy 2.0 + Alembic, Repository Pattern, dados sintéticos; o mesmo banco guarda auditoria, checkpoints do LangGraph e os vetores do RAG (D15, D17); SQLite só em testes de lógica pura | SQLite no disco do Cloud Run (perde tudo a cada cold start); Neon |
| **D6** | LLM ↔ banco | Tools LangChain com consultas fixas e parametrizadas; **text-to-SQL vetado** | `SQLDatabaseChain` (vetado) |
| **D7** | Fluxos | LangGraph `StateGraph` + `PostgresSaver` (Supabase) + `interrupt()` (human-in-the-loop), em passos de no máximo uma chamada ao LLM (D16) | Cadeias lineares |
| **D8** | Dataset | PubMedQA (PQA-L) + MedQuAD filtrado + corpus interno sintético pt-BR | Só dados públicos em inglês |
| **D9** | Anonimização | Regex pt-BR + spaCy `pt_core_news_lg`, pseudônimos consistentes, *gate* de PII residual | Microsoft Presidio |
| **D10** | Avaliação | Base vs FT (PubMedQA, MedQuAD, LLM-as-judge interno), RAG (citação/faithfulness), red-team, fluxos | RAGAS completo |
| **D11** | Embeddings do RAG | Escolhidos por ablação no gold set entre `all-MiniLM-L6-v2` (atual), `paraphrase-multilingual-MiniLM-L12-v2` e `multilingual-e5-small` (todos de 384 dimensões), pesando memória e cold start do backend; o escolhido vai embutido na imagem. Parte da D17 | Manter o atual sem medir |
| **D12** | Otimização de hiperparâmetros do fine-tuning | **Otimização bayesiana multifidelidade:** Optuna TPE + poda Hyperband em treinos curtos (proxy), com warm start a partir da config padrão de QLoRA; depois top-3 + padrão em fidelidade total e escolha por score composto no `val`. Detalhes na [F3](F03-fine-tuning-qlora.md#estratégia-de-otimização-de-hiperparâmetros-d12) | AG da Fase 2 (≈ 800 avaliações, inviável para LLM), grid manual ou 2–3 treinos manuais |
| **D13** | Seleção do modelo ativo do assistente | **Scorecard pré-registrado** (métricas, conjuntos, pisos, metas, pesos e gates congelados na F0, antes de qualquer treino), aplicado igualmente a todos os candidatos na F10; resultados publicados num registro de modelos e exibidos no **painel admin**, onde um `ADMIN` ativa o modelo (só candidatos elegíveis e disponíveis; troca auditada). Detalhes no [scorecard de modelos](00-scorecard-modelos.md) | Escolha informal, sem métricas fixas |
| **D14** | Orçamento | **Projeto inteiro no free tier ou ≤ R$5/mês** (meta: R$0–2): treino no computador pessoal, serving em CPU com escala a zero (cold start aceito; custo estimado com base em ~5 h/mês de uso), alerta de orçamento, limpeza do Artifact Registry, PyTorch CPU-only no backend. Detalhes em [custos e FinOps](00-custos-finops.md) | Serviços pagos por hora (GPU, endpoints dedicados, bancos gerenciados) |
| **D15** | Persistência | **Supabase (Postgres gratuito)** para prontuário, auditoria, sugestões, alertas, checkpoints e vetores: sobrevive a cold starts e é o mesmo para todas as instâncias. O projeto gratuito pausa após 7 dias sem uso, então um workflow semanal do GitHub Actions faz um `SELECT 1`. Conexão pelo pooler em modo transação. Dados sintéticos | Neon (sem pausa); SQLite + cópia no Cloud Storage; aceitar o reset |
| **D16** | Frontend ↔ API | **Mesma origem via Firebase Hosting:** rewrite de `/api/**` para o Cloud Run, cookie de sessão `__session` first-party (`SameSite=Strict`), respostas `Cache-Control: private, no-store`. Toda rota autenticada responde em menos de 60 s (limite do Hosting): o `/ask` devolve 503 `AST-022` na hora se o modelo estiver carregando, e os fluxos avançam em passos. Endpoints públicos legados seguem direto no `run.app` | Gateway nginx no Cloud Run (sem limite de 60 s, mas troca o Hosting); domínio próprio (custo) |
| **D17** | Vetorização | pgvector no Supabase; chunking por seção e por tokens com cabeçalho contextual; embeddings de 384 dimensões escolhidos por ablação; busca híbrida (vetor + texto em português, fusão RRF); rerank só se a ablação justificar; versões do corpus trocadas sem indisponibilidade. Detalhes na [estratégia de vetorização](00-vetorizacao-rag.md) | Chroma no disco da imagem; só busca vetorial, sem medir |

---

## 3. Matriz de Rastreabilidade (PDF → Fases)

| Requisito / Entregável | F0 | F1 | F2 | F3 | F4 | F5 | F6 | F7 | F8 | F9 | F10 | F11 |
| :--- | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: |
| R1.1 Protocolos no fine-tuning | | ● | ● | ● | | | | | | | | |
| R1.2 FAQ de médicos | | ● | ● | ● | | | | | | | | |
| R1.3 Laudos, receitas, procedimentos | | ● | ● | ● | | | | | | | | |
| R1.4 Preprocessing, anonimização, curadoria | | | ● | | | | | | | | | |
| R2.1 Pipeline LangChain com LLM customizada | | | | ○ | | | | ● | | | | |
| R2.2 Consulta a prontuários/registros | | | | | ● | | | ● | | | | |
| R2.3 Contexto atualizado do paciente | | | | | ● | | | ● | ● | | | |
| R3.1 Limites de atuação | ○ | | | | | ● | | ● | ● | ● | | |
| R3.2 Logging e auditoria | | | | | | ● | | ● | ● | ● | | |
| R3.3 Explainability / fontes | | | | | | ● | ● | ● | | ● | | |
| R4.1 Modularização Python | ● | ● | ● | ● | ● | ● | ● | ● | ● | ● | | |
| R4.2 README completo | | | | | | | | | | | | ● |
| E1 Pipeline de fine-tuning | | | ● | ● | | | | | | | | |
| E2 Integração LangChain | | | | | | | ● | ● | | | | |
| E3 Fluxos LangGraph | | | | | | | | | ● | | | |
| E4 Dataset anonimizado/sintético | | ● | ● | | ● | | | | | | | |
| E5–E7 Relatório (fine-tuning, assistente, diagrama) | | ○ | ○ | ○ | | ○ | ○ | ○ | ○ | | | ● |
| E8 Avaliação e análise de resultados | | | | | | | | | | | ● | ● |
| E9 Vídeo de até 15 min | | | | | | | | | | | | ● |

● = entrega principal · ○ = entrega parcial (ex.: a seção do relatório escrita no fechamento da própria fase)

---

## 4. Estrutura de Diretórios Alvo (R4.1) — com a fase que cria cada parte

```
backend/
├── app/
│   ├── core/
│   │   ├── settings.py, pii_patterns.py                 # F0
│   │   ├── logging_config.py, trace.py, exception_handlers.py   # F5
│   │   └── security.py                                  # F9
│   ├── db/ session.py, models.py, seed.py               # F4
│   ├── repositories/ patient, exam, suggestion, alert, audit, records_adapter.py   # F4
│   ├── assistant/
│   │   ├── errors.py, bootstrap.py                      # F0 (bootstrap evolui até a F9)
│   │   ├── schemas/ records.py (F4), answer.py + audit.py + guardrails.py (F5), retrieval.py (F6), flow.py (F8)
│   │   ├── ports.py                                     # F4 (records) + F5 (guards/audit) + F6 (retriever) + F7 (llm/drafter)
│   │   ├── audit/ audit_logger.py, pii_masker.py, sinks.py, db_sink.py        # F5
│   │   ├── guardrails/ input_guard, scope_policy, prescription_guard, citation_guard, output_guard   # F5
│   │   ├── retrieval/ embeddings, protocol_retriever, query_rewriter, context_formatter       # F6
│   │   ├── llm/ registry.py (F3); active_model.py, active_model_store.py, provider.py, cloud_run_auth.py, warmup.py (F7); prompts/, tools/, chains/   # F7
│   │   └── graph/ state, alert_rules, interaction_rules, nodes, patient_intake_flow, checkpointing, export_diagram   # F8
│   ├── services/ assistant_service.py (F7), flow_service.py (F8), model_selection_service.py (F9)
│   └── api/ envelope.py, dependencies/rate_limit.py, routers/{auth,assistant,admin_audit,admin_models}.py   # F9
├── finetuning/                                          # F1–F3 (laboratório offline, fora da imagem Docker)
│   ├── schemas.py, io.py, collectors/, synthetic/       # F1
│   ├── preprocessing/, prepare_dataset.py               # F2
│   ├── config.py, data_module.py, train_qlora.py, merge_and_export.py, register_candidates.py, config/, scripts/, README.md   # F3
│   ├── hpo/ search_space, pruning_callback, objective, selection, run_hpo, report   # F3 (Optuna TPE + Hyperband)
│   ├── triage.py   # F3 (triagem dos 5 modelos base → finalistas)
│   └── evaluate_model.py                                # F10
├── data/finetuning/{raw (gitignore), synthetic, processed, reports}/   # F1–F2
├── weights/llm/ run_*.json, loss_*.png, experiments_summary.json, hpo/<candidate_id>/{trials.csv, best_params.json, stage2_comparison.json, *.png}, registry/<candidate_id>.json, triage/   # F3 (scorecard gravado na F10)
├── knowledge_base/ extract.py, chunking.py, ingest_docs.py, evaluate_retrieval.py, config/vectorization.yaml, internal_protocols/   # F6 (vetores no Supabase; vector_db/ removido)
├── llm_service/ Dockerfile (`llama-swap` + `llama-server` CPU), render_config.py   # F3 (imagem do serviço healthai-llm)
├── migrations/ (Alembic: prontuário, papéis, RLS, pgvector, protocol_chunks, checkpoints)   # F4, F6, F8
├── evaluation/ datasets/, harness/, results/, run_all.py, scorecard/ (model_scorecard.yaml na F0; runner na F10)   # F5 (red-team), F6 (gold RAG), F10 (harness + scorecard)
├── tests/ conftest.py (F0) + finetuning/, db/, assistant/, api/, evaluation/   # cada fase a sua subpasta
└── requirements.txt / requirements-training.txt / requirements-dev.txt   # F0
frontend/src/app/ pages/medical-assistant/, components/assistant/*, services/assistant.service.ts, models/assistant.models.ts   # F9
docs/fase3/ secoes/*.md (fechamento de cada fase), diagramas/, relatorio-tecnico-fase3.md, roteiro-video-apresentacao.md   # F11 consolida
```

---

## 5. Catálogo Preliminar de Regras de Negócio (formalizado na F0)

> Arquivo: `.agents/docs/business_rules/BR-030-assistente-medico.md`, continuando a numeração depois do último código em uso (`P-034`).

| Código | Regra |
| :--- | :--- |
| **P-040** | O assistente **NUNCA** emite prescrição ou conduta definitiva. Toda sugestão terapêutica nasce `PENDENTE_VALIDACAO_MEDICA` e só vira `APROVADA` com a aprovação de um médico identificado. |
| **P-041** | Toda resposta clínica DEVE citar ≥ 1 fonte (documento + página/seção, ou campo do prontuário). Sem base: "Não há informações suficientes nos protocolos disponíveis." |
| **P-042** | Escopo restrito: saúde da mulher (oncologia mamária, SOP) e protocolos internos; fora do escopo → recusa padronizada. |
| **P-043** | Minimização: só os campos clínicos necessários entram no prompt, pseudonimizados (sem nome, CPF ou contato). |
| **P-044** | Todo evento (pergunta, recuperação, tool, guardrail, decisão humana, modelo usado) gera auditoria com `trace_id`, sem PII e sem objetos inteiros. |
| **P-045** | Alertas obrigatórios: exame pendente acima do SLA, resultado crítico (ex.: BI-RADS ≥ 4) sem conduta, interação/contraindicação na sugestão. |
| **P-046** | Só o perfil `MEDICO` usa o assistente e aprova condutas; a aprovação registra o aprovador. |
| **P-047** | Nenhum registro com PII residual entra no dataset de treino; o gate descarta e contabiliza. |
| **P-048** | LLM customizada indisponível → fallback; o modelo efetivamente usado aparece em `meta.model` e no log. |
| **P-049** | Um candidato só pode ser ativado se passar em **todos** os gates do scorecard pré-registrado (prescrição direta 0%, bloqueio de injection ≥ 95%, recusa fora de escopo ≥ 90%, citação ≥ 90%, PII vazada 0, uso estimado dentro do free tier, latência p95 ≤ 45 s) e se o scorecard tiver sido calculado com o YAML vigente. |
| **P-050** | Só o perfil `ADMIN` troca o modelo ativo do assistente, pelo painel; toda troca gera auditoria `MODEL_ACTIVATED` com admin, modelo anterior, modelo novo, score e hash do scorecard. |
| **P-051** | Em produção, o modelo ativo do assistente é **sempre um candidato fine-tuned** servido pelo serviço `healthai-llm`. O Gemini (free tier) só responde como contingência, **só para perguntas sem dados de paciente** (sem `patient_code` e sem PII detectada pelo `pii_masker` no texto), gerando `LLM_FALLBACK` e alerta no painel; com `patient_code` e o fine-tuned indisponível, a resposta é 503 (`AST-021`), sem enviar dados clínicos à API gratuita. |
| **P-052** | Quando o sistema acorda de um cold start, o backend dispara automaticamente, em paralelo e sem atrasar a própria inicialização, o carregamento do modelo escolhido no painel admin no `healthai-llm`. A troca de modelo no painel também dispara o carregamento do novo modelo. Cada carregamento gera o evento `LLM_WARMUP`. |

---

## 6. Dúvidas Resolvidas / Em Aberto

- **Dados reais do hospital?** Não há. Os PDFs de `knowledge_base/docs/` fazem o papel dos protocolos internos, e FAQ, laudos, receitas e procedimentos serão **sintéticos** (atende o E4 sem risco LGPD no treino).
- **D1 ❓ (lista de candidatos):** aprovada no checkpoint da F0, junto com o scorecard (D13). **D3 ❓ e D4 ❓** seguem a D14: treino no computador pessoal e serving em CPU no free tier (cold start aceito); o fine-tuned em produção não é opcional, e o ❓ restante é só confirmar a latência medida na F3.
- **Tela no frontend?** Sim (F9): chat com citações + painel de aprovação. Se o prazo apertar, pode ser reduzida ao Swagger.
- **"Coordenado com LangChain" vs "Fluxos do LangGraph":** o LangGraph orquestra os fluxos e os nós usam cadeias LCEL e tools LangChain (atende E2 e E3).
