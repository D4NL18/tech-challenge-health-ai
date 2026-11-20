# F9 — API, Autenticação de Médicos e Interface do Assistente (R3.1–R3.3 expostos, E9)

> [Índice](INDEX.md) · Anterior: [← F8](F08-fluxos-langgraph.md) · Próxima: [F10 →](F10-avaliacao.md)  
> Referências: [Contexto e decisões](00-contexto-e-decisoes.md) · [Modelo de execução](00-modelo-de-execucao.md)  
> **Status:** ⏳ Não iniciada

## Objetivo

Expor assistente, fluxos, alertas e auditoria via API REST com envelope; migrar a autenticação para cookie HttpOnly com papéis `ADMIN`/`MEDICO`; criar a tela do assistente com citações e painel de aprovação; e permitir ao `ADMIN` comparar os candidatos pelo scorecard e ativar o modelo do assistente no painel admin; tudo atrás do Firebase Hosting, na mesma origem do frontend (D16), com cada requisição abaixo do limite de 60 s.

## Ponto de partida
- **Backend:** `admin.py` (`OAuth2PasswordBearer`, HS256, um admin vindo do `.env`, `/admin/login` devolvendo o token no corpo, `get_current_admin()` em `/admin/metrics`, `/admin/matrix`, `/admin/active-models`, `/admin/genetic-experiments`); `CORSMiddleware(allow_credentials=True)` com origens explícitas; `AdvancedExponentialRateLimiter` global; `GET/POST /admin/active-models` com `weights/active_models.json` (o GET não exige autenticação — dívida L13).
- **Frontend:** `auth.service.ts` (`localStorage`, `admin_jwt_token`); `auth.interceptor.ts` (Bearer); `AuthGuard` síncrono; `admin-login`/`admin-dashboard`; `app.routes.ts` (4 rotas); nav em `app.html`; `components/{button,card,input}`; chat da página `medical-routes` como referência; `DESIGN_SYSTEM.md` + `prontuario-kit.html`; `admin-dashboard` com seções por tipo de modelo, cards com métricas e `setAsActive()` via `AdminService.setActiveModel` (padrão reaproveitado na seção de modelos do assistente); `environment.prod.ts` aponta direto para o `run.app` (outro site, o que impede cookie de sessão) e o `firebase.json` só tem o rewrite da SPA.
- **Fases anteriores:** `AssistantService` (F7), `FlowService` (F8), `AlertRepository`/`AuditRepository` (F4), handlers + `trace_id` (F5), `bootstrap.py` (F0–F8), `settings.doctor_*` (F0); `ModelRegistry` (F3); `ActiveModelResolver` e `is_available` (F7); scorecard pré-registrado (F0, [scorecard de modelos](00-scorecard-modelos.md)); `LLMWarmupService` (F7, aquecimento automático).

## Etapas e agentes
- **Etapas ativas:** 2 (contrato da API, Design Plan, desenho do auth, revisão de minimização), **Checkpoint**, 3, 4 (segurança, UX, LGPD).
- **Acionados:**

| Agente | Papel nesta fase |
| :--- | :--- |
| `architect` | Contrato REST (`api_contracts/assistant.md`) com envelope, exemplos e erros |
| `designer` | Design Plan da tela do assistente e da seção **Modelo do Assistente** do admin (8 estados, filtro Anti-IA) |
| `security` | Dono do auth: cookie HttpOnly, CSRF, papéis, troca de modelo só por `ADMIN`; auditoria OWASP final |
| `privacy-officer` | Anti-overfetching no contrato (Etapa 2) e na UI (Etapa 4), com veto |
| `tester` (×2) | Contrato da API + auth / frontend (services, guard, componentes) |
| `developer` (×2) | Backend (auth, routers, rate limit, bootstrap, seleção de modelo) / frontend Angular (tela do assistente + seção de modelos do admin) |
| `ux-reviewer` | Fidelidade ao Design Plan, estados, acessibilidade |
| `reviewer` | Quality Gate |

- **Não acionados:** `ai-specialist` (sem mudança em LLM; o scorecard só é exibido aqui, o cálculo é na F10), `dba` (sem schema novo: as tabelas de usuários não são necessárias, porque os usuários de demo vêm do `settings`), `devops` (deploy só na F11).

## Execução em rodadas

| Rodada | Agente (paralelo) | Tarefas | Arquivos exclusivos |
| :--- | :--- | :--- | :--- |
| **R1** (Etapa 2) | `architect` | Contrato REST (endpoints da tabela abaixo, DTOs, envelope, paginação, códigos `AST-*`) | `.agents/docs/api_contracts/assistant.md` |
| | `designer` | Design Plan: chat + painel do paciente, `CitationCard`, `GuardrailBadge` ("Requer validação médica"), `AlertList`, `FlowTimeline`, `ApprovalDialog`, `TraceIdChip`; 8 estados; só `patient_code`; seção **Modelo do Assistente** no `admin-dashboard` (tabela comparativa, barras por grupo do scorecard, gates com motivo, badges Recomendado/Ativo/Indisponível, diálogo de confirmação com a diferença em score, latência e custo) | `.agents/docs/design/plans/assistente_medico.md` |
| | `security` | Desenho do auth na mesma origem (D16): cookie `__session` (o único que o Firebase Hosting repassa ao Cloud Run; `HttpOnly`, `Secure`, `SameSite=Strict`), CSRF via `X-Requested-With`, `Cache-Control: private, no-store` nas respostas da API, papéis, transição do Bearer | `.agents/docs/adr/ADR-008-auth-cookie-httponly.md` |
| | `privacy-officer` | Revisão de minimização do contrato (respostas sem campos desnecessários) | Parecer no contrato |
| **Checkpoint** | Orquestrador | Contrato + Design Plan + ADR-008 | — |
| **R2** (TDD) | `tester#1` | Testes de contrato (`TestClient`) de cada endpoint/erro; auth 401/403/CSRF; paginação; rate limit; login do admin com cookie `__session`; `Cache-Control: private, no-store`; `/ask` com o modelo carregando → 503 `AST-022` sem chamar o LLM; `advance`; `model-status` (só aciona o aquecimento se `COLD`, idempotente); endpoints de modelos (só `ADMIN`, candidato inelegível ou com scorecard desatualizado → 422, indisponível → 409, troca auditada, `POST /admin/active-models` rejeitando `assistant_llm`) | `tests/api/*` |
| | `tester#2` | Specs Angular: `AuthService` (sem `localStorage`), interceptor (`X-Requested-With`, sem depender de `withCredentials`), guard por papel, `AssistantService`, `AdminService` (modelos do assistente), componentes "burros" (incluindo a seção de modelos do admin) | `frontend/src/app/**/*.spec.ts` |
| **R3** (código) | `developer#1` (back) | 9.1–9.6 + 9.10 | `app/core/security.py`, `app/services/model_selection_service.py`, `app/api/routers/admin_models.py`, `app/api/{envelope.py, dependencies/rate_limit.py}`, `app/api/routers/{auth,assistant,admin_audit}.py`, `app/api/routers/admin.py`, `bootstrap.py` |
| | `developer#2` (front) | 9.7–9.9 + 9.11 + 9.12 | `frontend/src/app/{services,interceptors,guards,models,pages/medical-assistant,components/assistant}/*`, `pages/admin-login/*`, `pages/admin-dashboard/*`, `components/admin/assistant-models/*`, `app.routes.ts`, `app.html`, `frontend/firebase.json`, `frontend/proxy.conf.json`, `frontend/src/environments/*` |
| **R4** (Etapa 4) | `security` ∥ `ux-reviewer` ∥ `privacy-officer` ∥ `reviewer` ∥ `tester` | OWASP + checagem de `localStorage` ∥ Design Plan e 8 estados ∥ UI e API sem PII (**veto**) ∥ revisão ∥ suítes back e front + `npm run build` + Auto-Healer | — |
| **R5** (Fechamento) | Orquestrador | Merge + `STATE.md` | — |

## Endpoints

| Método | Rota | Papel | Service |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/auth/login` · `/api/auth/logout` · `GET /api/auth/me` | público / autenticado | `core/security.py` |
| `POST` | `/api/v1/assistant/ask` | `MEDICO` | `AssistantService.ask` |
| `POST` | `/api/v1/assistant/flows/patient-intake` | `MEDICO` | `FlowService.start_intake` |
| `GET` | `/api/v1/assistant/flows/{thread_id}` | `MEDICO` | `FlowService.get_status` |
| `POST` | `/api/v1/assistant/flows/{thread_id}/advance` | `MEDICO` | `FlowService.advance` (no máximo uma chamada ao LLM) |
| `POST` | `/api/v1/assistant/flows/{thread_id}/decision` | `MEDICO` | `FlowService.decide` (`reviewer = user.username`) |
| `GET` | `/api/v1/assistant/alerts?limit&offset` | `MEDICO` | `PatientRecordsPort.list_alerts` |
| `GET` | `/api/admin/audit-events?trace_id&limit&offset` | `ADMIN` | `AuditRepository.list` |
| `GET` | `/api/admin/assistant-models` | `ADMIN` | `ModelSelectionService.list_candidates` (registro + disponibilidade + ativo + recomendado) |
| `PUT` | `/api/admin/assistant-models/active` | `ADMIN` | `ModelSelectionService.activate(candidate_id, admin)` |
| `GET` | `/api/v1/assistant/model-status` | `MEDICO` ou `ADMIN` | `LLMWarmupService.status()`; se o ativo estiver `COLD` (o `healthai-llm` voltou a dormir), dispara `trigger` (idempotente) |

> Todas as rotas acima passam pelo Firebase Hosting (`/api/**`, mesma origem do frontend) e respondem em menos de 60 s. Os endpoints públicos legados (`/api/v1/anamnesis`, `/api/v1/routes`) continuam sendo chamados direto no `run.app`, sem o limite do Hosting.

## Código passo a passo
- [ ] **9.1 — `core/security.py`:** `Role{ADMIN, MEDICO}`, `AuthUser`, `authenticate(username, password)` (`hmac.compare_digest`; usuários do `settings`; **sem valores padrão inseguros**: sem `JWT_SECRET` ou senhas configuradas, o backend não sobe, ao contrário do `admin.py` atual, que cai em `super-secret-key`/`admin`), `create_access_token(user)`, `set_auth_cookie(response, token)` (cookie `__session`, `HttpOnly`, `Secure`, `SameSite=Strict`, `Path=/`), `clear_auth_cookie(response)`, `get_current_user(request)` (lê o cookie; Bearer só com `ALLOW_BEARER_TRANSITION=true`), `require_role(*roles)` → 401/403; `require_csrf_header` em métodos não-GET.
- [ ] **9.2 — `routers/auth.py`:** login seta o cookie e devolve `{data: {username, role}}`; logout; `me`. O router `admin.py` passa a ser montado também em `/api/admin` (no Hosting, o `/admin/...` colidiria com as rotas `/admin/...` do Angular), e `get_current_admin` vira `require_role(Role.ADMIN)` e `/admin/login` passa a ser alias do novo login (**BREAKING** para o frontend).
- [ ] **9.3 — `api/envelope.py`:** `ok(data, meta=None)` → `{"data": …, "meta": {"timestamp", "trace_id", "model"?}}` e `paginated(rows, total, limit, offset)`; middleware que põe `Cache-Control: private, no-store` em toda resposta de `/api` (o Hosting não pode guardar em cache resposta autenticada).
- [ ] **9.4 — `routers/assistant.py`:** controllers finos (recebe → service → `ok()`), DTOs validados (`question` 1–1000 caracteres; `patient_code` com regex); handlers `async`, chamando o service com `ainvoke`.
- [ ] **9.5 — `routers/admin_audit.py` + `dependencies/rate_limit.py`:** auditoria paginada; `LLMRateLimit(max_per_minute=10)` por usuário nas rotas que chamam LLM (o limiter global continua). O uvicorn passa a rodar com `--proxy-headers --forwarded-allow-ips='*'`: atrás do proxy do Cloud Run, sem isso todos os clientes aparecem com o mesmo IP e dividem o limite global. O `model-status`, consultado por polling, fica fora do limite global.
- [ ] **9.6 — Bootstrap final:** `register_assistant(app)` registra `auth`, `assistant`, `admin_audit` (o stub 501 sai); com `ASSISTANT_ENABLED=false` só o `auth` fica ativo.
- [ ] **9.7 — Auth no frontend:** `AuthService` sem `localStorage` (`login()`, `me()` alimentando `signal<AuthUser | null>`, `logout()`); interceptor com `X-Requested-With` (na mesma origem, o cookie vai sozinho); `AuthGuard` assíncrono com checagem de papel (`data: {roles: [...]}`); `admin-login` ajustado.
- [ ] **9.8 — Modelos e service:** `assistant.models.ts` (interfaces do contrato, sem `any`); `AssistantService` (`ask`, `startIntake`, `getFlow`, `decide`, `listAlerts`).
- [ ] **9.9 — Tela:** página `medical-assistant` (container smart) + componentes "burros" `assistant-chat`, `citation-card`, `guardrail-badge`, `flow-panel`, `alert-list`, `approval-dialog`, `trace-id-chip`; rota `/assistant` com guard `MEDICO`; link no nav; chip de status do modelo ativo ("carregando" / "pronto", via `model-status`) no topo do chat; a página chama o `model-status` ao abrir e quando o campo de pergunta recebe foco, e, enquanto o modelo não estiver pronto, o envio mostra "carregando o modelo".
- [ ] **9.10 — Backend da escolha de modelo:** `services/model_selection_service.py` com `list_candidates() -> list[CandidateView]` (registro + `is_available`, lido do registro e da configuração publicada, sem acordar o `healthai-llm` + `is_active`, `is_recommended` e `is_stale`, que indica scorecard calculado com outro YAML); `recommend(candidates)` (maior score entre elegíveis e disponíveis; desempate pela menor latência p95); `activate(candidate_id, admin)` → valida se é fine-tuned (P-051), elegibilidade e scorecard atual (`AST-051`, 422) e disponibilidade (`AST-052`, 409) → grava a escolha no `ActiveModelStore` (Cloud Storage) → auditoria `MODEL_ACTIVATED` com admin, anterior, novo, score e hash do scorecard (P-050) → `LLMWarmupService.trigger(novo)`, para o modelo escolhido já começar a carregar na troca. `routers/admin_models.py` com `require_role(Role.ADMIN)` e envelope. O `POST /admin/active-models` legado rejeita a chave `assistant_llm`, para não contornar os gates.
- [ ] **9.11 — Seção "Modelo do Assistente Médico" no `admin-dashboard`:** container no componente existente + componentes "burros" `assistant-model-table` (candidato, tipo, score composto, nota por grupo, latência p95 (quente), cold start medido, custo por 1.000 respostas, gates ✓/✗ com motivo, disponibilidade), `scorecard-bars` (barras por grupo), `model-detail-drawer` (todas as métricas, hiperparâmetros, links dos gráficos da HPO) e `activate-model-dialog` (diferença em relação ao ativo). Botão **Ativar** desabilitado para inelegível, indisponível ou scorecard desatualizado (tooltip com o motivo); badges Recomendado e Ativo; referências (base, FT padrão e Gemini) aparecem só para comparação, sem botão (P-051); banner **"Produção em contingência"** quando houve `LLM_FALLBACK` recente, lido da auditoria. `AdminService` ganha `listAssistantModels()` e `activateAssistantModel(id)`, tipados (sem `any`); após **Ativar**, chip de status com polling de `model-status` até o novo modelo ficar "pronto".
- [ ] **9.12 — Mesma origem via Firebase Hosting (D16):** o `firebase.json` ganha, antes do rewrite da SPA, `{"source": "/api/**", "run": {"serviceId": "healthai-diagnostics", "region": "us-central1"}}`; o `environment` passa a ter `secureApiUrl: '/api'` (mesma origem: auth, admin e assistente) e mantém `apiUrl` direto no `run.app` só para os endpoints públicos legados; em desenvolvimento, um `proxy.conf.json` do Angular manda `/api` para `localhost:8000`. **Orçamento de 60 s:** o `/ask` responde 503 `AST-022` (`Retry-After`) na hora se o modelo não estiver `READY` e dispara o aquecimento; a tela reenvia sozinha quando o `model-status` fica pronto; os fluxos avançam por `advance` (F8); o gate de latência do scorecard (p95 ≤ 45 s) garante a folga.

## Critérios de aceite

Nenhum token em `localStorage`; rotas novas com envelope; erros com `{error, code, trace_id}`; só `MEDICO` decide; `npm run build` com código 0; painel admin funcionando com o cookie; citações, alertas e aprovação visíveis na tela; só `ADMIN` troca o modelo do assistente, só para candidatos elegíveis, disponíveis e com scorecard atual, sempre com auditoria; frontend e API na mesma origem pelo Firebase Hosting; nenhuma rota autenticada passa de 60 s.

## Audit

(1) `POST /decision` sem cookie → 401; com `ADMIN` → 403; sem `X-Requested-With` → 403; (2) `GET /alerts` sem `limit` → 20 + `meta.total`; (3) LLM falhando → erro sem stack; (4) `grep -r "localStorage" frontend/src` sem token; (5) 11ª chamada/minuto ao `/ask` → 429; (6) fluxo completo na UI com o seed "BI-RADS 4"; (7) `PUT /admin/assistant-models/active` com candidato reprovado num gate → 422 `AST-051`; com `MEDICO` → 403; troca válida → evento `MODEL_ACTIVATED` e `meta.model` do `/ask` seguinte com o novo modelo; (8) em produção, o login pelo `web.app` mantém a sessão (cookie first-party) e nenhuma rota autenticada passa de 60 s.

## Commits

`docs(api): adiciona contrato do assistente` · `docs(design): adiciona design plan do assistente medico` · `feat(auth)!: migra jwt para cookie httponly com papeis admin e medico` (rodapé `BREAKING CHANGE:` explicando que o frontend deixa de enviar Bearer) · `feat(api): expoe endpoints do assistente e fluxos com envelope` · `feat(api): adiciona trilha de auditoria paginada para admin` · `feat(frontend): adapta auth ao cookie e guard por papel` · `feat(frontend): cria tela do assistente com fontes e aprovacao` · `feat(api): adiciona selecao do modelo do assistente com gates e auditoria (P-049, P-050)` · `feat(frontend): adiciona secao de modelos do assistente no painel admin` · `feat(frontend)!: chama a api pela mesma origem via firebase hosting`

## Entrega para a F10/F11

Sistema ponta a ponta (com os fine-tuned servidos por `healthai-llm` e fallback Gemini só para perguntas sem dados de paciente); painel admin pronto para exibir os scorecards que a F10 vai gravar no registro.
