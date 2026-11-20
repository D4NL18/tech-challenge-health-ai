# Status Atual do Desenvolvimento (Context Window)

Este documento é mantido exclusivamente pelo **Orquestrador**. Ele serve como uma memória persistente do estado exato onde a conversa e a funcionalidade se encontram, prevenindo que as diretrizes se percam em contextos (prompts) longos.

## Tarefa em Andamento — Fase 3 (planejada em 2026-11-07; F0 iniciada em 2026-11-13)
- **Feature/Entidade:** Fase 3 — Assistente Médico Personalizado (Fine-tuning + LangChain + LangGraph)
- **Plano Mestre:** `.agents/docs/plans/INDEX.md` (v3 — um arquivo por fase em `.agents/docs/plans/F00…F11`; fases **sequenciais**, paralelismo só entre agentes dentro de cada fase, em rodadas com arquivos exclusivos)
- **Triagem:** T1 (Full-Stack + IA + PII). Os agentes são escolhidos fase a fase (matriz em `.agents/docs/plans/00-modelo-de-execucao.md`); o `product-owner` não é acionado (backlog já fatiado).
- **Etapa Atual do Fluxo:** F0 em execução (ver "F0 — Execução" abaixo). Decisões registradas no planejamento: a lista de candidatos (D1) e o scorecard pré-registrado (D13) são aprovados no checkpoint da F0; D3/D4 precisam estar tomadas antes da F3 (D4: fine-tuned obrigatório em produção, servido em CPU no Cloud Run; D14: projeto inteiro no free tier ou ≤ R$5/mês, Cloud Run com cold start aceito e custo estimado com base em ~5 h/mês de uso, sem limite; D3: treino no computador pessoal com GTX 1660 SUPER 6 GB; D15: Supabase; D16: API na mesma origem via Firebase Hosting; D17: vetorização com pgvector).
- **Branch de integração planejada:** `feature/fase3` (uma branch por fase, mesclada ao fim de cada uma; nada direto na `master`).

### Fases (uma de cada vez)
| Fase | Agentes acionados | Checkpoint | Status |
| :--- | :--- | :-: | :--- |
| F0 Fundação | analyst, architect, ai-specialist, privacy-officer, devops, tester, developer, reviewer (+ finance-advisor de apoio na R1) | ✓ | 🔄 R1 em execução |
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
| R4 (Fechamento) | Orquestrador | 🔄 commits atômicos na `feature/fase3-f0-fundacao` e merge local em `feature/fase3`; sem push |

### Pendências que ficam abertas depois da F0
- **Auditoria 2 (imagem Docker):** daemon do Docker parado; só checagem estática. Rodar `docker build backend/` e conferir `pip list` antes da F1.
- **Auditoria 3 (CI bloqueia deploy):** `needs: [changes, test]` conferido por leitura; prova real só depois do push (autorização do usuário).
- **Runbook A0–A7:** conferência da conta de faturamento bloqueada — a ativação da Cloud Billing API foi negada pelo modo automático; o usuário precisa rodá-la ou conferir no Console. Artifact Registry com 3,5 GB (~US$0,30/mês fora do free tier): A2 resolve.
- **Tier da chave do Gemini:** conferir no AI Studio.
- **Dívidas técnicas (T4):** `app/ml/vision.py:105` usa `json` sem import (modelo de visão não carrega, erro engolido); modelos scikit-learn salvos com 1.5.2 e carregados com o pin 1.3.2 (`InconsistentVersionWarning`); GA do VRP não garante balanceamento CRITICAL/HIGH (~10% das execuções sem semente).
- **Sugestões do reviewer** (S-1…S-12 em `STATE_F0_reviewer.md`), em especial S-6 (`REQUIRE_TEST_DB=1` no CI antes da F4), S-7 (`::add-mask::` no keep-alive) e S-12 (`.gcloudignore` em `backend/`, o upload do Cloud Build pode estar levando `datasets.zip` de 5 GB).

### Decisões do checkpoint F0 (aprovadas pelo usuário em 2026-11-20)
1. **D1 — candidatos:** `llama32-1b`, `qwen25-1_5b`, `qwen3-1_7b` (thinking desligado), `gemma3-1b`, `tucano-2b4`; Gemini só como referência não selecionável. Ids e licenças conferidos no HF no início da F3.
2. **D13 — scorecard congelado:** piso de custo US$4,77/1.000 respostas (opção B do ADR-009); `pinned_model_id: gemini-3.8-flash` (também vale para `gemini_fallback_model`); `sha256 4236cf76…2a04`, cópia versionada em `backend/evaluation/scorecard/model_scorecard.sha256`; `.gitattributes` força LF no YAML. Desempate proposto pelo `ai-specialist` aceito.
3. **Aquecimento (A1 do architect):** dispara em thread própria a partir do bootstrap; o `main.py` continua com 2 linhas.
4. **Geração lenta:** timeout do cliente abaixo de 55 s com código `AST-*` próprio (F7); 504 ocasional pelo Firebase Hosting aceito como risco residual.
5. **Privacidade:** retenção de logs 30 dias; checkpoints 7 dias após conclusão / 30 dias parados; auditoria pela vida do projeto. Auditoria guarda só metadados da pergunta. `actor_id`/`actor_role` no lugar de identidade (PA-07; `username` validado por regex até a F9, depois UUID) — o `analyst` ajusta a redação de P-040/P-044/P-046 no BR-030. `pii_patterns.py` com 15 padrões + `PATIENT_CODE_PATTERN` (seção 17 do RIPD). Nenhum dado real em nenhuma fase. Supabase em `us-east-1`.
6. **D14 — orçamento:** teto R$5/mês, alerta calculado a R$6,00/US$. Runbook `tasks/F0-runbook-infra.md` aprovado, começando pela A0 (só leitura).
7. **Entrypoint:** `backend/app/main.py` (o plano citava `backend/main.py`).
8. **Pendente do usuário:** confirmar no AI Studio o tier da chave do Gemini (se pago, preço dobra em 2027-01-01).

### Agentes acionados e pulados na F0
- **Acionados (plano):** `analyst`, `architect`, `ai-specialist`, `privacy-officer`, `devops` (R1); `tester`, `developer` (R2); `reviewer`, `tester` (R3).
- **Acrescentado pelo Orquestrador:** `finance-advisor` na R1, só para conferir free tiers e preços de lista nas páginas oficiais (tarefa do plano para a F0; o `devops` não tem ferramenta web). Entrega em `.agents/docs/STATE_F0_finance-advisor.md`.
- **Pulados:** `product-owner` (backlog já fatiado em US-13…US-22), `dba` (o schema é desenhado na F4), `designer`/`ux-reviewer` (sem UI), `security` (sem superfície nova; auth só na F9), `ai-governance-auditor` (ainda não há modelo).

### Ocorrências
- **2026-11-13 — hooks do GSD:** os hooks globais do GSD em `C:\Users\PC\.claude\settings.json` (sintaxe PowerShell executada em bash) bloqueavam `Write`, `Edit` e `Bash` para o Orquestrador e para os subagentes. O usuário decidiu não usar mais o GSD: hooks e statusLine removidos do `settings.json`; agentes, skills, hooks e núcleo do GSD movidos para `C:\Users\PC\.claude-gsd-backup-20261113\` (backup reversível, nada apagado).
- **`.agents/` está no `.gitignore`:** ADRs, BR-030, glossário e RIPD não são versionados. Dos commits `docs(adr)` previstos na F0, só `backend/evaluation/scorecard/model_scorecard.yaml` entra no git. Levar ao checkpoint.
- **Ações que alteram contas externas** (alerta de orçamento, limpeza do Artifact Registry, bucket, service account, projeto Supabase, secrets, deploy temporário, `git push`) e o **smoke de GPU no WSL2 (passo 0.9)** só acontecem depois da aprovação do usuário no checkpoint. Na R1 o `devops` entrega os arquivos locais e o runbook.
- **`.agents/hooks.json` e `.agents/mcp_config.json`** ainda são genéricos (npm lint/test; Postgres de exemplo). Sincronizar com a stack (pytest, Postgres local do `docker-compose.dev.yml`) no fechamento da F0.
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
