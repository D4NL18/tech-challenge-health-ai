# Status Atual do Desenvolvimento (Context Window)

Este documento é mantido exclusivamente pelo **Orquestrador**. Ele serve como uma memória persistente do estado exato onde a conversa e a funcionalidade se encontram, prevenindo que as diretrizes se percam em contextos (prompts) longos.

## Tarefa em Andamento — Fase 3 (planejada em 2026-11-07; F0 iniciada em 2026-11-13)
- **Feature/Entidade:** Fase 3 — Assistente Médico Personalizado (Fine-tuning + LangChain + LangGraph)
- **Plano Mestre:** `.agents/docs/plans/INDEX.md` (v3 — um arquivo por fase em `.agents/docs/plans/F00…F11`; fases **sequenciais**, paralelismo só entre agentes dentro de cada fase, em rodadas com arquivos exclusivos)
- **Triagem:** T1 (Full-Stack + IA + PII). Os agentes são escolhidos fase a fase (matriz em `.agents/docs/plans/00-modelo-de-execucao.md`); o `product-owner` não é acionado (backlog já fatiado).
- **Etapa Atual do Fluxo:** **F0 concluída em 2026-11-21**; próxima fase: **F1 — Coleta e Geração do Corpus** (`.agents/docs/plans/F01-corpus.md`). Decisões consolidadas em `.agents/docs/KNOWLEDGE_GRAPH.md`.
- **Branch de integração planejada:** `feature/fase3` (uma branch por fase, mesclada ao fim de cada uma; nada direto na `master`).

### Fases (uma de cada vez)
| Fase | Agentes acionados | Checkpoint | Status |
| :--- | :--- | :-: | :--- |
| F0 Fundação | analyst, architect, ai-specialist, privacy-officer, devops, tester, developer, reviewer (+ finance-advisor de apoio na R1) | ✓ | ✅ Concluída em 2026-11-20 (pendências de nuvem com o usuário) |
| F1 Corpus | ai-specialist, tester×2, developer×2, reviewer | — | ⏳ |
| F2 Anonimização e curadoria | privacy-officer, ai-specialist, tester×2, developer×2, reviewer | ✓ | ⏳ |
| F3 Fine-tuning QLoRA + HPO (Optuna) por candidato + triagem de 5 modelos + serviço único `healthai-llm` (troca sob demanda, aquecimento automático) | ai-specialist, tester×2, developer×3, devops, security, reviewer | — | ⏳ (requer D1 aprovada na F0 + D3/D4) |
| F4 Prontuário (Supabase) | dba, architect, privacy-officer, security, tester×2, developer×2, reviewer | ✓ | ⏳ |
| F5 Segurança e auditoria | security, architect, privacy-officer, tester×2, developer×2, reviewer | — | ⏳ |
| F6 RAG: vetorização e busca híbrida (pgvector) | ai-specialist, dba, security, tester×2, developer×2, reviewer | — | ⏳ |
| F7 Assistente LangChain | ai-specialist, security, privacy-officer, tester×2, developer×2, reviewer | — | ⏳ |
| F8 Fluxos LangGraph | architect, ai-specialist, tester×2, developer×2, reviewer | ✓ | ⏳ |
| F9 API, auth e UI | architect, designer, security, privacy-officer, tester×2, developer×2, ux-reviewer, reviewer | ✓ | ⏳ |
| F10 Avaliação + scorecard dos candidatos | ai-specialist, tester, developer×2, ai-governance-auditor, reviewer | ✓ (escolha do modelo no painel) | ⏳ |
| F11 Documentação e release | devops, developer, orchestrator, reviewer | — | ⏳ |
## F0 — Execução (Fundação, Governança e Infraestrutura de Testes)
- **Plano da fase:** `.agents/docs/plans/F00-fundacao.md` · **Triagem:** T1 (Full-Stack + IA + PII), só as etapas 1, 2, checkpoint, 3, 4 e 5 (CI) que a F0 exige.
- **Branch:** `feature/fase3-f0-fundacao`, criada de `feature/fase3`, criada da `master` (`fa08e23`). Ambas locais, sem push. A alteração local do usuário em `AGENTS.md` segue intocada e fora dos commits.
- **Estados isolados da rodada:** `.agents/docs/STATE_F0_<agente>.md` (mesclados aqui ao fim de cada rodada).

| Rodada | Quem | Estado |
| :--- | :--- | :--- |
| R1 (Etapas 1–2) | `analyst`, `architect`, `ai-specialist`, `privacy-officer`, `devops`, `finance-advisor` (apoio) | ✅ Concluída em 2026-11-20 neste computador (reexecutada do zero em 2026-11-16 por decisão do usuário; as entregas parciais do outro computador devem ser descartadas). Entregas: BR-030, GLOSSARY, RIPD, ADR-001…006, 009…012, ARCHITECTURE.md, scorecard (`sha256 644f5b02…ad27`), requirements (27 testes verdes em venv limpo, Python 3.12.1), CI com job `test`, keep-alive a cada 3 dias, compose dev, runbook `tasks/F0-runbook-infra.md`. Estados isolados em `STATE_F0_*.md` |
| Checkpoint | Orquestrador → usuário (D1, D13, D3, D4, D14, D15, D16 + ações na nuvem) | ✅ Aprovado em 2026-11-20 (recomendações do Orquestrador, ver "Decisões do checkpoint F0") |
| R2 (Etapa 3) | `tester`, `developer` | ✅ 2026-11-20: `app/core/{settings,pii_patterns}.py`, `app/assistant/{errors,bootstrap}.py`, 2 linhas no `app/main.py`, `pytest.ini`, `conftest.py`, 269 testes novos |
| R3 (Etapa 4) | `reviewer` ∥ `tester` | ✅ APROVADO COM RESSALVAS; I-1 (semente só no teste do VRP), I-2 (`AST-050`) e I-3 (teste de configuração inválida) corrigidos pelo Orquestrador; I-4: hash versionado em `model_scorecard.sha256`, `.agents/` segue fora do git. Venv limpo: 298 passed, 1 skipped, 5/5 execuções estáveis; stub real 501 `AST-050`; cold start local 7,5 s |
| R4 (Fechamento) | Orquestrador | ✅ 2026-11-20: 11 commits atômicos na `feature/fase3-f0-fundacao`, merge em `feature/fase3`, push das duas branches. CI no GitHub verde na `feature/fase3` (run 44781593316); prova do bloqueio com teste quebrado (run 44780797129: job `test` falhou, deploys pulados; branch descartável apagada). Imagem Docker auditada (4,13 GB, sem libs de treino nem dados). Testes de integração com pgvector: 2 passed. Passo 0.9 (A8, A9, A10 local) executado: ver `STATE_F0_smoke-gpu.md` |

### Pendências que ficam abertas depois da F0
- **`compute_dtype` — decidido em 2026-11-21:** fp32 com peft + trl (opção B, aprovada pelo usuário). ADR-001 Adendo 1; contingência de VRAM no `tucano-2b4` com Unsloth mantendo fp32.
- **`llama-swap` — decidido em 2026-11-21 pela regra do ADR-002 (ponto 5):** sai; `llama-server` em modo router com `ctx-size` fixo no preset de cada modelo. ADR-002 Adendo 1.
- **Ações de nuvem (runbook A0–A7 e A10 no Cloud Run):** não executadas. A ativação da Cloud Billing API foi negada pelo modo automático; o usuário roda os comandos do runbook. Artifact Registry com 3,5 GB (~US$0,30/mês).
- **Supabase (A6):** a conta só tem a organização "Fitoherb" (projeto "Fitoherb Website"); o projeto do HealthAI não deve ser criado lá. O usuário cria uma organização pessoal e o projeto em `us-east-1`.
- **Prova do bloqueio de deploy na `master`:** feita com `workflow_dispatch` numa branch descartável (job `test` falhou, deploys pulados); a prova na própria `master` só acontece no primeiro push para ela.
- **Porta 5433 ocupada nesta máquina** por outro Postgres: usar `DEV_POSTGRES_PORT=5434` e `TEST_DATABASE_URL=postgresql+psycopg://healthai:healthai_dev@localhost:5434/healthai_dev`.
- **Imagem Docker de 4,13 GB:** `nvidia` (205 MB) numa imagem só de CPU e `kubernetes` (119 MB, via `chromadb`); revisar quando a F6 remover o `chromadb`.
- **Tier da chave do Gemini:** conferir no AI Studio.
- **Dívidas técnicas (T4):** `app/ml/vision.py:105` sem `import json`; modelos scikit-learn salvos com 1.5.2 e carregados com 1.3.2; GA do VRP sem garantia de balanceamento. Sessão de hotfix proposta.
- **Sugestões do reviewer:** S-6 (`REQUIRE_TEST_DB=1` no CI), S-7 (`::add-mask::` no keep-alive) e S-12 (`backend/.gcloudignore`) aplicadas em 2026-11-21. Seguem abertas S-1…S-5 e S-8…S-11 em `STATE_F0_reviewer.md` (fases F5, F7, F9, F11).
- **`backend/venv`:** reinstalado em 2026-11-21 com `requirements.txt` + `requirements-dev.txt` (usado pelo hook de `.agents/hooks.json`).

### Agentes acionados e pulados na F0
- **Acionados (plano):** `analyst`, `architect`, `ai-specialist`, `privacy-officer`, `devops` (R1); `tester`, `developer` (R2); `reviewer`, `tester` (R3).
- **Acrescentado pelo Orquestrador:** `finance-advisor` na R1, só para conferir free tiers e preços de lista nas páginas oficiais (tarefa do plano para a F0; o `devops` não tem ferramenta web). Entrega em `.agents/docs/STATE_F0_finance-advisor.md`.
- **Pulados:** `product-owner` (backlog já fatiado em US-13…US-22), `dba` (o schema é desenhado na F4), `designer`/`ux-reviewer` (sem UI), `security` (sem superfície nova; auth só na F9), `ai-governance-auditor` (ainda não há modelo).

### Ocorrências
- **2026-11-13 — hooks do GSD:** os hooks globais do GSD em `C:\Users\PC\.claude\settings.json` (sintaxe PowerShell executada em bash) bloqueavam `Write`, `Edit` e `Bash` para o Orquestrador e para os subagentes. O usuário decidiu não usar mais o GSD: hooks e statusLine removidos do `settings.json`; agentes, skills, hooks e núcleo do GSD movidos para `C:\Users\PC\.claude-gsd-backup-20261113\` (backup reversível, nada apagado).
- **`.agents/` está no `.gitignore`:** ADRs, BR-030, glossário e RIPD não são versionados. Dos commits `docs(adr)` previstos na F0, só `backend/evaluation/scorecard/model_scorecard.yaml` entra no git. Levar ao checkpoint.
- **Ações que alteram contas externas** (alerta de orçamento, limpeza do Artifact Registry, bucket, service account, projeto Supabase, secrets, deploy temporário, `git push`) e o **smoke de GPU no WSL2 (passo 0.9)** só acontecem depois da aprovação do usuário no checkpoint. Na R1 o `devops` entrega os arquivos locais e o runbook.
- **`.agents/hooks.json` e `.agents/mcp_config.json`:** sincronizados com a stack em 2026-11-20 (pytest do backend; Postgres do `docker-compose.dev.yml`).
- **2026-11-13 — pausa da R1 (rate limit):** os 6 subagentes da R1 (`analyst`, `architect`, `ai-specialist`, `privacy-officer`, `devops`, `finance-advisor`) atingiram o limite de 5h do Claude antes de gravar qualquer arquivo (`STATE_F0_*.md`, ADRs, `BR-030`, scorecard, runbooks). Estado e planos salvos em commit na branch `feature/fase3-f0-fundacao` para retomada a partir da R1 em outro ambiente.
- **2026-11-16 — retomada no computador principal (GTX 1660 SUPER 6 GB, WSL2 Ubuntu):** a R1 foi reexecutada numa sessão Remote Control em **outro computador** (GTX 1650 4 GB, WSL só com `docker-desktop`), que parou de novo por rate limit. Lá: onda 1 (`analyst`, `privacy-officer`, `finance-advisor`) concluída; onda 2 (`architect`, `ai-specialist`, `devops`) interrompida. As entregas (~6.400 linhas) estão **só no disco daquele computador**, sem commit nem push; o remoto continua em `9fc0385`. Para trazê-las: no outro computador, `git add -A` + `git add -f .agents/docs` (a pasta está no `.gitignore`), commit e `git push origin feature/fase3-f0-fundacao`.
- **Linha de base dos testes antigos (medida na outra sessão):** os 27 testes passam em venv limpo desde que `matplotlib` seja declarado no `requirements.txt` e o `numpy` fique abaixo de 2.x (o `matplotlib` sem restrição puxa o numpy 2 e quebra o `scikit-learn==1.3.2`). O Python global não tem `google-genai`. Repassar ao `devops` na onda 2.
- **Smoke de GPU (passo 0.9):** só roda neste computador (o outro não atende a D3).

## Última Tarefa Concluída (Fase 2)
- **Feature/Entidade:** Auditoria de Camadas e Garantia de Não Sobreposição do Header (.app-header)
- **Branch Atual:** `main` / `feature/fase2-tech-challenge`
- **Etapa Atual do Fluxo:** Etapa 4 (Quality Gate & Refinamento Visual UX)
- **Diretrizes Ativas Atendidas:**
  1. **Hierarquia Rigorosa de Camadas (Z-Index):**
     - `.app-header` elevado para `z-index: var(--z-nav, 1500)` com fundo opaco em [app.scss](file:///c:/GitHub/tech-challenge-health-ai/frontend/src/app/app.scss).
     - Escala global padronizada em [styles.scss](file:///c:/GitHub/tech-challenge-health-ai/frontend/src/styles.scss): `--z-base: 0; --z-map: 1; --z-sticky: 200; --z-dropdown: 500; --z-nav: 1500; --z-drawer: 2000; --z-modal: 3000; --z-toast: 4000; --z-tooltip: 5000;`.
     - `.search-bar-wrapper` (`z-index: 100`) e `.search-dropdown` (`z-index: 110`) em [medical-routes.component.scss](file:///c:/GitHub/tech-challenge-health-ai/frontend/src/app/pages/medical-routes/medical-routes.component.scss) calibrados para ficarem confortavelmente acima do mapa (`z-index: 1`), mas rigorosamente abaixo do `.app-header` (`z-index: 1500`), garantindo que todo conteúdo da página deslize sob o cabeçalho ao rolar a página.
  2. **Isolamento de Stacking Context:**
     - `.map-card` com `isolation: isolate; position: relative; z-index: 1;`, impedindo vazamento de z-index de controles internos do Leaflet.
  3. **100% Visual / 0% Lógica:** Zero alterações em regras TypeScript ou serviços.
  4. **Compilação Validada:** `npm --prefix frontend run build` executado com código 0.

## Progresso do Workflow (Checklist da Pipeline de 12 Passos)
- [x] 1. Quebra de Escopo no Backlog (Product Owner) - *ROADMAP.md atualizado*
- [x] 2. Especificação e Regras de Negócio P-XXX (Analista) - *BR-010 e BR-020*
- [x] 3. Projetar Arquitetura, Contratos, UI e Revisão de Privacy by Design (Arquiteto, Designer & AI Specialist)
- [x] 4. Modelagem de Dados Segura e Cache Local SQLite (DBA)
- [x] 5. Planejar Tarefas e Decomposição de Checklist (Arquiteto)
- [x] 6. Desenvolver Testes Unitários TDD - Pré-código (Tester)
- [x] 7. Executar Código na Branch de Feature (Desenvolvedor) - *Alinhamento de layout concluído*
- [x] 8. Code Review de Clean Code & Auditoria de Código LGPD (Reviewer & Privacy Officer)
- [x] 9. UX Review / Vibe Check e Filtro Anti-IA Slop (UX Reviewer) - *Aprovado*
- [x] 10. Validação de Testes QA e Loop de Auto-Healer (Tester) - *Frontend build código 0; 27 testes backend passando*
- [x] 11. Auditoria de Cibersegurança e Red Teaming (SecOps)
- [x] 12. Validação de CI/CD, Documentação e Relatórios Técnicos (DevOps)
