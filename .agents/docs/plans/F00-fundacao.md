# F0 — Fundação, Governança e Infraestrutura de Testes

> [Índice](INDEX.md) · Anterior: — · Próxima: [F1 →](F01-corpus.md)  
> Referências: [Contexto e decisões](00-contexto-e-decisoes.md) · [Modelo de execução](00-modelo-de-execucao.md)  
> **Status:** 🔄 Em andamento — R1 (Etapas 1–2) despachada em 2026-11-13; checkpoint com o usuário em seguida

## Objetivo

Deixar o repositório pronto para a Fase 3: regras, ADRs, RIPD, dependências, CI que bloqueia deploy quebrado, infraestrutura de testes, esqueleto de pastas e o ponto único de ligação do assistente no `main.py`.

## Ponto de partida
- `requirements.txt` sem `langgraph`/`langchain-google-genai`/`langchain-huggingface`/`langchain-text-splitters` e sem versões fixas no ecossistema LangChain (L6).
- `main.py`: 3 routers e um `lifespan` que só carrega o `inference_service`.
- `backend/tests/`: 27 testes, sem `conftest.py` nem markers.
- `Dockerfile` copia `training_scripts/` e `knowledge_base/`; o `deploy.yml` faz deploy sem testes.
- `ARCHITECTURE.md` ainda é template; não há `GLOSSARY.md` nem ADRs. O `ROADMAP.md` já tem US-13…US-22.

## Etapas e agentes
- **Etapas ativas:** 1 (regras de negócio), 2 (ADRs, RIPD), **Checkpoint**, 3 (infra de testes + esqueleto), 4 (revisão), 5 (só CI, sem release).
- **Acionados:**

| Agente | Papel nesta fase |
| :--- | :--- |
| `analyst` | Formaliza P-040…P-052 e o glossário |
| `architect` | ADRs de arquitetura, `ARCHITECTURE.md`, desenho do bootstrap/settings |
| `ai-specialist` | ADRs de modelo, dataset e avaliação |
| `privacy-officer` | RIPD da Fase 3 e lista oficial de entidades PII |
| `devops` | Dependências, `.dockerignore`/`.gitignore`, job de testes no CI, branch `feature/fase3` |
| `tester` | `pytest.ini`, `conftest.py`, markers, estrutura de `tests/` |
| `developer` | Esqueleto de pastas, `settings.py`, `pii_patterns.py`, `errors.py`, `bootstrap.py`, hook no `main.py` |
| `reviewer` | Quality Gate do PR |

- **Não acionados:** `product-owner` (backlog já fatiado), `dba` (o schema é desenhado na F4, que é quem o usa), `designer`/`ux-reviewer` (sem UI), `security` (sem superfície nova; auth só na F9), `ai-governance-auditor` (sem modelo ainda).

## Execução em rodadas

| Rodada | Agente (paralelo) | Tarefas | Arquivos exclusivos |
| :--- | :--- | :--- | :--- |
| **R1** (Etapas 1–2) | `analyst` | BR-030 (P-040…052 no template), `GLOSSARY.md` (Conduta, Protocolo, Exame Pendente, Alerta Clínico, Validação Humana, Pseudônimo, Trace) | `.agents/docs/business_rules/BR-030-assistente-medico.md`, `.agents/docs/GLOSSARY.md` |
| | `architect` | ADR-002 (fine-tuned em produção no serviço único `healthai-llm` em CPU, com `llama-swap` para trocar entre finalistas sob demanda e aquecimento automático no cold start (P-052), fallback de contingência sem dados de paciente, D4/P-048/P-051), ADR-003 (prontuário + acesso do LLM, D5/D6), ADR-004 (LangGraph + HITL, D7), ADR-011 (persistência no Supabase, D5/D15), ADR-012 (API na mesma origem via Firebase Hosting e orçamento de 60 s, D16), `ARCHITECTURE.md` real (camadas, assistente, bootstrap, flags) | `.agents/docs/adr/ADR-002…004`, `ADR-011`, `ADR-012`, `.agents/docs/architecture/ARCHITECTURE.md` |
| | `ai-specialist` | ADR-001 (pool de triagem e regra dos finalistas + QLoRA + ambiente + HPO, D1–D3 e D12), ADR-005 (dataset + anonimização, D8/D9), ADR-006 (avaliação, D10/D11), **ADR-009 (seleção do modelo por scorecard, D13)** e o **scorecard pré-registrado** (passo 0.8) | `.agents/docs/adr/ADR-001`, `ADR-005`, `ADR-006`, `ADR-009`, `backend/evaluation/scorecard/model_scorecard.yaml` |
| | `privacy-officer` | RIPD (dados tratados, base legal: tutela da saúde, art. 11, II, "f" da LGPD; minimização; retenção de logs e checkpoints; dados de paciente nunca enviados ao free tier do Gemini; Supabase (AWS) como operador, só com dados sintéticos); lista de entidades PII pt-BR | `.agents/docs/privacy/RIPD_assistente_medico.md` |
| | `devops` | Passos 0.6, 0.7, 0.9, 0.10 + ADR-010 (orçamento ≤ R$5/mês, D14) | `.agents/docs/adr/ADR-010-orcamento-free-tier.md`, `requirements*.txt`, `.dockerignore`, `.gitignore`, `.github/workflows/{deploy,supabase-keepalive}.yml`, `docker-compose.dev.yml` |
| **Checkpoint** | Orquestrador | Resumo dos ADRs + aprovação do pool de triagem e da regra dos finalistas (D1) e do scorecard pré-registrado (métricas, pisos, metas, pesos e gates) + decisões D3 (treino no computador pessoal), D4 (CPU no Cloud Run), D14 (orçamento ≤ R$5/mês), D15 (Supabase) e D16 (API na mesma origem) | — |
| **R2** (Etapa 3) | `tester` | Passo 0.5 | `backend/pytest.ini`, `backend/tests/conftest.py`, `backend/tests/{finetuning,db,assistant,api,evaluation}/__init__.py` |
| | `developer` | Passos 0.1–0.4 | `app/core/{settings,pii_patterns}.py`, `app/assistant/{errors,bootstrap}.py`, esqueleto de pastas, `main.py` (2 linhas), `.env.example` |
| **R3** (Etapa 4) | `reviewer` ∥ `tester` | Revisão do PR ∥ suíte antiga verde, teste de CI (branch com teste quebrado não faz deploy) | — |
| **R4** (Fechamento) | Orquestrador | Merge em `feature/fase3`, `STATE.md` | — |

## Código passo a passo
- [ ] **0.1 — `app/core/settings.py`:** `AssistantSettings(BaseSettings)` com `assistant_enabled`, `assistant_default_candidate` (fine-tuned usado antes de existir escolha no painel), `active_model_store_uri` (objeto no Cloud Storage em produção; arquivo local em dev), `llm_service_url` (URL do `healthai-llm` em produção ou do `llama-swap` local em dev), `llm_auth_mode` (`none` | `cloud_run_id_token`), `gemini_fallback_model`, `database_url` (pooler do Supabase em modo transação), `database_direct_url` (migrações), `embedding_model`, `corpus_version`, `rag_min_score`, `exam_sla_days`, `doctor_username`, `doctor_password`. `get_settings()` com cache.
- [ ] **0.2 — `app/core/pii_patterns.py`:** `CPF_PATTERN`, `CNS_PATTERN`, `RG_PATTERN`, `CRM_PATTERN`, `PHONE_BR_PATTERN`, `EMAIL_PATTERN`, `CEP_PATTERN`, `DATE_PATTERN` e `PII_PATTERNS: dict[str, re.Pattern]` (lista do `privacy-officer`). Fonte única para a F2 (dataset) e a F5 (logs).
- [ ] **0.3 — `app/assistant/errors.py`:** `AssistantDomainError(code, http_status, public_message)` + faixas de código reservadas por fase (F4 `AST-4xx`, F5 `AST-001…019`, F7/F8 `AST-020…049`, F9 `AST-050…069`).
- [ ] **0.4 — `app/assistant/bootstrap.py`:** `register_assistant(app)` (por enquanto registra um router stub `/api/v1/assistant/*` → 501 quando `assistant_enabled=False`) e `init_assistant_resources()` (no-op). **Única edição no `main.py`:** chamar `register_assistant(app)` depois dos `include_router` e `init_assistant_resources()` como **primeira** instrução do `lifespan`, antes de `inference_service.load_all_models()`, para o aquecimento do LLM (P-052, F7) correr em paralelo com o carregamento dos modelos legados. Dali em diante, cada fase liga o que produz pelo bootstrap.
- [ ] **0.5 — Infra de testes:** `pytest.ini` (`testpaths = tests`; markers `slow`, `gpu`, `llm_live`, `integration`); `conftest.py` com `sqlite_session` (SQLite em memória, lógica pura), `postgres_session` (Postgres local com pgvector, marker `integration`), `fake_chat_model` (`FakeListChatModel` com respostas roteirizadas) e `settings_override`; subpastas por área.
- [ ] **0.6 — Dependências:** `requirements.txt` com versões fixas de `langchain-core`, `langchain-community`, `langchain-text-splitters`, `langchain-huggingface`, `langchain-google-genai`, `langchain-openai` (só como cliente do protocolo compatível do `llama-server`; nenhuma chamada à OpenAI), `langgraph`, `langgraph-checkpoint-postgres`, `sqlalchemy>=2`, `psycopg[binary]` (v3), `pgvector` (o `chromadb` atual continua até a F6 removê-lo), `alembic`, `pydantic-settings`, `rank-bm25`, `google-auth` (ID token para o `healthai-llm`), `google-cloud-storage` (escolha persistida do modelo ativo); `requirements-training.txt` com `peft`, `trl`, `optuna`, `bitsandbytes`, `datasets`, `accelerate`, `spacy`, `evaluate`, `rouge-score`, `bert-score`, `huggingface_hub`; `requirements-dev.txt` com `pytest`, `pytest-cov`. **PyTorch CPU-only** no backend (índice de wheels CPU), para reduzir a imagem e o custo do Artifact Registry.
- [ ] **0.7 — Infra:** `.dockerignore` exclui `finetuning/`, `data/finetuning/`, `evaluation/`, `tests/`; `.gitignore` exclui `backend/data/finetuning/raw/`, `*.gguf`, `**/adapters/`, `*.safetensors`; `deploy.yml` ganha o job `test` (`pytest -m "not slow and not gpu and not llm_live"`) e `needs: test` nos deploys, com cache do pip e filtro de caminhos (o job de fine-tuning, com `requirements-training.txt`, só roda quando `finetuning/` muda; `bitsandbytes` e Unsloth com import tardio, para o smoke rodar sem GPU); criar `feature/fase3`. **Guardrails de custo (D14):** conferir os free tiers vigentes; alerta de orçamento de R$5/mês (50%, 90%, 100%, real e previsto); política de limpeza do Artifact Registry (só as 2 versões mais recentes; nunca por idade); bucket `healthai-llm-models` em us-central1 com lifecycle e um objeto de configuração para a escolha do modelo ativo; `min-instances 0` e `max-instances` ≤ 2 no backend; service account do backend. Ver [custos e FinOps](00-custos-finops.md).
- [ ] **0.8 — Scorecard pré-registrado (`backend/evaluation/scorecard/model_scorecard.yaml`):** lista de candidatos; métricas por grupo com conjunto, nível (modelo/sistema), piso, meta e peso; gates eliminatórios; regra de desempate; parâmetros de custo (preço por token das APIs, com data da consulta, e custo/hora da máquina de referência). O `sha256` do arquivo é registrado no ADR-009, e **o arquivo não muda depois do checkpoint** (mudança = adendo no ADR + reavaliação de todos os candidatos). Ver [scorecard de modelos](00-scorecard-modelos.md).
- [ ] **0.9 — Ambiente de treino local (computador pessoal (GTX 1660 SUPER 6 GB, i5-11400, 32 GB RAM, WSL2 Ubuntu)):** no WSL2 Ubuntu, Python com `requirements-training.txt`, CUDA visível (`torch.cuda.is_available()` e `nvidia-smi` no WSL), bitsandbytes funcionando e Unsloth instalado, se compatível; **smoke de QLoRA de 20 passos no `Llama-3.2-1B`** medindo VRAM, tempo por passo e se o fp16 gera NaN (decide o `compute_dtype`); Docker Desktop disponível para o `llama-server` local; teste local com dois GGUF para verificar se o `llama-server` da versão escolhida já troca de modelo sozinho ou se o `llama-swap` é necessário. É um teste de risco feito cedo, para a F3 não descobrir problema de ambiente no meio da busca. Também mede o **fator de conversão de latência**: o mesmo GGUF de referência no `llama-server` local (4 threads) e num deploy temporário no Cloud Run (4 vCPU, poucos minutos), porque o i5-11400 tende a ser mais rápido que os vCPUs do Cloud Run; a regra de latência da triagem (F3) usa esse fator.
- [ ] **0.10 — Supabase (D15):** projeto no free tier na região mais próxima do us-central1 (ex.: `us-east-1`); extensões `vector` e `unaccent`; segredos `DATABASE_URL` (pooler em modo transação) e `DATABASE_DIRECT_URL` no GitHub Actions e no Cloud Run; **keep-alive** `.github/workflows/supabase-keepalive.yml` (cron semanal com um `SELECT 1`, porque o projeto gratuito pausa após 7 dias sem uso); `docker-compose.dev.yml` com `pgvector/pgvector:pg16` para desenvolvimento e testes de integração, e o mesmo Postgres como service container no CI.

## Critérios de aceite

Os 27 testes antigos verdes com o novo `conftest.py`; `/api/v1/assistant/ask` → 501 com a flag desligada; a imagem Docker sem `peft`/`trl`/`finetuning/`; CI bloqueando deploy em teste quebrado; ADRs, RIPD, lista de candidatos e scorecard aprovados no checkpoint; hash do scorecard registrado no ADR-009; alerta de orçamento de R$5 ativo e limpeza do Artifact Registry configurada.

## Audit

(1) venv limpo + `pip install -r requirements.txt -r requirements-dev.txt` + `pytest` verde; (2) `docker build backend/` + inspeção do `pip list`; (3) push com teste quebrado → `deploy-*` não roda.

## Commits

`docs(adr): registra decisoes da fase 3` · `docs(adr): pre-registra scorecard de selecao do modelo` · `chore(deps): fixa ecossistema langchain e separa deps de treino` · `ci: executa testes antes do deploy` · `test: adiciona conftest, markers e estrutura de testes` · `feat(assistant): adiciona settings, padroes de pii e bootstrap do assistente`

## Entrega para a F1

Dependências de treino, `.gitignore` de dados brutos, ADR-001/005 (o que coletar e como anonimizar), infraestrutura de testes.
