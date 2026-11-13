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
| R1 (Etapas 1–2) | `analyst`, `architect`, `ai-specialist`, `privacy-officer`, `devops`, `finance-advisor` (apoio) | ⏸️ Interrompida por rate limit antes de gerar entregas (pronta para reexecutar) |
| Checkpoint | Orquestrador → usuário (D1, D13, D3, D4, D14, D15, D16 + ações na nuvem) | ⏳ |
| R2 (Etapa 3) | `tester`, `developer` | ⏳ |
| R3 (Etapa 4) | `reviewer` ∥ `tester` | ⏳ |
| R4 (Fechamento) | Orquestrador | ⏳ |

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
