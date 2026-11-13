# F11 — Documentação Final, Relatório, Deploy e Vídeo (R4.2, E5–E9)

> [Índice](INDEX.md) · Anterior: [← F10](F10-avaliacao.md) · Próxima: —  
> Referências: [Contexto e decisões](00-contexto-e-decisoes.md) · [Modelo de execução](00-modelo-de-execucao.md)  
> **Status:** ⏳ Não iniciada

## Objetivo

Consolidar o relatório técnico, completar os READMEs, publicar a versão com o assistente e preparar o roteiro do vídeo.

## Ponto de partida
- **Projeto:** `README.md`/`README_en.md` (Fases 1 e 2, "Como executar", 27 testes); estrutura de `docs/fase2/relatorio-tecnico-fase2.md` e `docs/fase2/roteiro-video-apresentacao.md`; `docs_en/`; `deploy.yml` (job `test` da F0; envs `GEMINI_API_KEY`, `OPENAI_API_KEY`, `ADMIN_*`, `JWT_SECRET`; `--max-instances 2 --memory 2Gi`); `Dockerfile`.
- **Fases anteriores:** seções `docs/fase3/secoes/01…07` (F1, F2, F3, F5, F6, F7, F8, F10); diagramas (F7, F8); resultados (F10); registro de modelos com scorecards e o modelo ativo escolhido (F10).

## Etapas e agentes
- **Etapas ativas:** 4 (revisão final) e 5 (release, CI, PR, compressão de contexto). Sem Etapas 1–3: não há código de produto novo.
- **Acionados:**

| Agente | Papel nesta fase |
| :--- | :--- |
| `devops` | Dono do release: envs/secrets, Dockerfile, deploy do backend usando o serviço `healthai-llm`, revisão final de custo, verificação de que produção responde com o fine-tuned, PR final |
| `developer` | READMEs PT/EN, `.env.example`, versão EN do relatório |
| `orchestrator` | Consolidação do relatório a partir das seções, roteiro do vídeo, `context-compressor`, reset do `STATE.md` |
| `reviewer` | Revisão final (docs fora da raiz, links, matriz de rastreabilidade) |

- **Não acionados:** todos os especialistas de domínio (o conteúdo técnico já foi escrito por eles no fechamento de cada fase), `tester` (o CI roda a suíte), `designer`/`ux-reviewer`.

## Execução em rodadas

| Rodada | Agente (paralelo) | Tarefas | Arquivos exclusivos |
| :--- | :--- | :--- | :--- |
| **R1** | `orchestrator` | 11.1 (relatório consolidado) + 11.4 (roteiro do vídeo) | `docs/fase3/relatorio-tecnico-fase3.md`, `docs/fase3/roteiro-video-apresentacao.md` |
| | `developer` | 11.2 (READMEs + `.env.example`) | `README.md`, `README_en.md`, `.env.example` |
| | `devops` | 11.3 (deploy) | `.github/workflows/deploy.yml`, `backend/Dockerfile`, `backend/.dockerignore` |
| **R2** | `developer` | Versão EN do relatório | `docs_en/fase3/technical-report-phase3.md` |
| **R3** (Etapa 4) | `reviewer` | Revisão final + [matriz de rastreabilidade](00-contexto-e-decisoes.md#3-matriz-de-rastreabilidade-pdf--fases) marcada com links | — |
| **R4** (Etapa 5) | `devops` ∥ `orchestrator` | PR `feature/fase3` → `master` ∥ `KNOWLEDGE_GRAPH.md` + reset do `STATE.md` | — |
| **Usuário** | — | Gravação do vídeo seguindo o roteiro | — |

## Passo a passo
- [ ] **11.1 — Relatório consolidado:** introdução e problema → processo de fine-tuning, incluindo a otimização de hiperparâmetros (tabela de estratégias, histórico, importância dos parâmetros, ganho sobre a config padrão) → arquitetura (diagrama geral + cadeia LCEL + fluxo LangGraph) → seções 01–07 → LGPD e ética → conclusão. Cobre E5, E6, E7 e E8.
- [ ] **11.2 — READMEs:** seção "Fase 3" com pré-requisitos (Python 3.12, Docker para o `llama-server` local; GPU NVIDIA com ≥ 6 GB só para treinar), variáveis novas (`ASSISTANT_*`, `RECORDS_DB_URL`, `DOCTOR_*`, `LLM_*`), passo a passo (preparar dataset → treinar localmente (WSL2 + GPU NVIDIA) → exportar o GGUF → subir o `llama-server` local → `alembic upgrade head` + seed → subir a API → `/assistant` → `run_all.py` → `pytest`), nova contagem de testes e links; e como comparar e ativar o modelo do assistente no painel admin; seção de custos (free tier, teto de R$5/mês e como conferir no billing).
- [ ] **11.3 — Deploy com o fine-tuned em produção (free tier):** envs do backend `ASSISTANT_ENABLED=true`, `LLM_SERVICE_URL=<URL do healthai-llm>`, `LLM_AUTH_MODE=cloud_run_id_token`, `ASSISTANT_DEFAULT_CANDIDATE=<fine-tuned escolhido na F10>`, `GEMINI_API_KEY` (só contingência, sem dados de paciente), `DOCTOR_*`, `DATABASE_URL` (segredo); backend com a service account que tem `run.invoker` no `healthai-llm` e leitura/escrita no objeto de configuração do modelo ativo; registro (`weights/llm/registry/`, com os nomes dos modelos no `llama-swap`) e `migrations/` na imagem; `alembic upgrade head` e seed idempotente rodando no deploy (conexão direta), não no startup; `firebase deploy` com o rewrite `/api/**` → Cloud Run (D16); `min-instances 0` e `max-instances` ≤ 2; versão final do `healthai-llm` via `deploy-llm.yml`. **Verificação pós-deploy obrigatória:** `/ask` em produção com `meta.model = healthai-med-<candidate_id>` e nenhum `LLM_FALLBACK`; depois de o sistema escalar a zero, a primeira requisição ao backend gera um `LLM_WARMUP`, e o modelo ativo fica pronto sem ação manual (P-052); o login pelo `web.app` mantém a sessão, e nenhuma rota autenticada passa de 60 s pelo Hosting. **Revisão final de custo:** billing do mês ≤ R$5, limpeza do Artifact Registry ativa ([custos e FinOps](00-custos-finops.md)). Documentar: dados no Supabase (persistem entre cold starts, com keep-alive semanal); cold start dos serviços de LLM (aceito: a primeira resposta depois de ocioso leva dezenas de segundos) e a estimativa de custo (~5 h/mês de uso cabem com folga no free tier).
- [ ] **11.4 — Roteiro (≤ 15 min, E9):** 0:00 problema e arquitetura · 1:30 dados, anonimização e treino (treino local na GTX 1660 SUPER, curvas, export GGUF) · 5:00 perguntas contextualizadas com citações · 7:30 fluxo LangGraph (paciente → pendências → alerta → sugestão → aprovação) · 11:00 logs com `trace_id` e guardrails bloqueando prescrição e injection · 12:30 painel admin: scorecard dos candidatos, ativação do fine-tuned e resposta em produção com `meta.model` do fine-tuned · 13:30 resultados e conclusão.
- [ ] **11.5 — Release:** PR final com a matriz de rastreabilidade marcada com links.

## Critérios e Audit

(1) alguém segue o README em máquina limpa e chega ao assistente respondendo com um fine-tuned (`llama-server` local com o GGUF, ou apontando para `healthai-llm` com ID token); (2) todos os R/E da matriz com link para o artefato; (3) vídeo ≤ 15:00 cobrindo os 4 pontos do PDF; (4) deploy só depois do CI verde; (5) produção responde com o fine-tuned (`meta.model`), verificado após o deploy; (6) billing do mês ≤ R$5.

## Commits

`docs(relatorio): consolida relatorio tecnico da fase 3` · `docs(readme): adiciona instrucoes completas da fase 3` · `ci: configura variaveis do assistente no deploy` · `docs(video): adiciona roteiro da apresentacao da fase 3`
