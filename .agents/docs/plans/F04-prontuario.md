# F4 — Base Estruturada de Prontuários e Registros (R2.2, R2.3, E4)

> [Índice](INDEX.md) · Anterior: [← F3](F03-fine-tuning-qlora.md) · Próxima: [F5 →](F05-seguranca-auditoria.md)  
> Referências: [Contexto e decisões](00-contexto-e-decisoes.md) · [Modelo de execução](00-modelo-de-execucao.md)  
> **Status:** ⏳ Não iniciada

## Objetivo

Criar no **Postgres do Supabase** a base relacional sintética que o assistente consulta (pacientes, exames, diagnósticos, medicações, sugestões de conduta, alertas e auditoria), acessada só por repositórios e exposta ao assistente por um port com dados minimizados.

## Ponto de partida
- **Projeto:** não há banco relacional; o único SQLite é `services/geo/geo_cache.py` (cache de rotas, que não muda). A base nova fica no **Postgres do Supabase (free tier, D15)**, com SQLAlchemy 2.0 + Alembic: sobrevive aos cold starts do Cloud Run e é a mesma para todas as instâncias.
- **Fases anteriores:** `settings.database_url`, projeto Supabase com as extensões `vector` e `unaccent` e o Postgres local de desenvolvimento em Docker, `errors.py` (faixa `AST-4xx`), fixtures `sqlite_session` e `postgres_session`, `bootstrap.init_assistant_resources()` (F0); RIPD (F0, minimização).

## Etapas e agentes
- **Etapas ativas:** 2 (schema, port, minimização), **Checkpoint** (schema), 3, 4 (com veto LGPD).
- **Acionados:**

| Agente | Papel nesta fase |
| :--- | :--- |
| `dba` | Dono: schema, índices, migração Alembic com travas anti-perda no Supabase, papéis de menor privilégio, RLS e seeds rotulados |
| `architect` | `PatientRecordsPort` e schemas de domínio (`PatientSnapshot` …) que o assistente vai consumir |
| `privacy-officer` | Regras de minimização do snapshot (P-043) e revisão dos seeds; veto na Etapa 4 |
| `security` | Credenciais do banco, papéis de menor privilégio e RLS (o banco agora é um serviço externo) |
| `tester` (×2) | Testes de repositório / testes de contrato do port |
| `developer` (×2) | Sessão + models + repositórios / adapter + seed + bootstrap |
| `reviewer` | Quality Gate (inclui a checagem básica de SQL injection) |

- **Não acionados:** `ai-specialist` (sem LLM aqui), `designer`/`ux-reviewer`, `devops` (o projeto Supabase e o keep-alive já vêm da F0).

## Execução em rodadas

| Rodada | Agente (paralelo) | Tarefas | Arquivos exclusivos |
| :--- | :--- | :--- | :--- |
| **R1** (Etapa 2) | `dba` | Schema das 8 tabelas, enums, índices e cenários de seed | `.agents/docs/db/prontuario.md` |
| | `architect` | 4.1 (port + schemas de domínio) | `app/assistant/ports.py`, `app/assistant/schemas/records.py` |
| | `privacy-officer` | Campos permitidos no snapshot e proibição de nome/contato no banco sintético | Adendo no RIPD |
| **Checkpoint** | Orquestrador | Schema + port | — |
| **R2** (TDD) | `tester#1` | Repositórios contra Postgres local com pgvector (marker `integration`; SQLite em memória só para lógica pura): contagem de queries, paginação, not-found, injection literal | `tests/db/test_repositories.py` |
| | `tester#2` | Teste de contrato do `PatientRecordsPort` (roda contra qualquer implementação) + seeds determinísticos | `tests/assistant/contract/test_patient_records_contract.py`, `tests/db/test_seed.py` |
| **R3** (código) | `developer#1` | 4.2, 4.3, 4.5 | `app/db/{session,models}.py`, `app/repositories/*_repository.py` |
| | `dba` | 4.4 (Alembic) e 4.7 (seeds + export `.sql`) | `backend/migrations/*`, `app/db/seed.py`, `.agents/docs/db/seeds/prontuario_seeds.sql` |
| **R4** (código) | `developer#2` | 4.6 (adapter) e 4.8 (ligar no bootstrap) | `app/repositories/records_adapter.py`, `app/assistant/bootstrap.py` |
| **R5** (Etapa 4) | `reviewer` ∥ `privacy-officer` ∥ `security` ∥ `tester` | Revisão ∥ auditoria de minimização (**veto**) ∥ papéis, RLS e credenciais ∥ suíte + Auto-Healer | — |
| **R6** (Fechamento) | Orquestrador | Merge + `STATE.md` | — |

## Código passo a passo
- [ ] **4.1 — Contratos (`schemas/records.py`, `ports.py`):** `PatientSnapshot{patient_code, birth_year, sex, active_diagnoses[], pending_exams[], recent_results[], active_medications[], risk_flags[]}`, `PendingExam`, `AlertDraft`, `SuggestionDraft`, `SuggestionDecision`; `PatientRecordsPort(Protocol)`: `get_snapshot(code)`, `list_pending_exams(code, page)`, `save_suggestion(draft, thread_id) -> id`, `set_suggestion_status(decision)`, `create_alerts(drafts) -> ids`, `list_alerts(page) -> Page`.
- [ ] **4.2 — `app/db/session.py`:** `build_engine(url)` com `psycopg` 3 pelo pooler do Supabase (Supavisor) em **modo transação**, `NullPool` (o pooler já faz o pool, e o Cloud Run escala instâncias) e prepared statements desligados (`prepare_threshold=None`, exigência do modo transação); `SessionFactory`; `session_scope()` (commit/rollback); `init_records_db()` só confere a conexão no startup. **Migrações e seed não rodam no startup**: rodam no deploy (F11) e pela CLI, na conexão direta.
- [ ] **4.3 — `app/db/models.py`:** `Base(DeclarativeBase)`; enums `ExamStatus`, `SuggestionStatus{PENDENTE_VALIDACAO_MEDICA, APROVADA, REJEITADA}`, `AlertSeverity`; tabelas `Patient`, `Encounter`, `Exam`, `Diagnosis`, `Medication`, `CareSuggestion`, `ClinicalAlert`, `AuditEventRow` (append-only); índice em toda FK + `(exams.patient_id, status)` e `(exams.status, due_date)`.
- [ ] **4.4 — Alembic:** `migrations/` + revisão `0001_prontuario_inicial` com `downgrade` seguro, `CREATE EXTENSION IF NOT EXISTS vector` e `unaccent`, papéis `healthai_app` (leitura e escrita só nas tabelas da aplicação) e `healthai_ingest` (escrita nos trechos do RAG), e **RLS ligada** em todas as tabelas, com políticas para esses papéis. As migrações usam a conexão direta (`database_direct_url`).
- [ ] **4.5 — Repositórios:** `PatientRepository.get_with_clinical_data(code)` (`selectinload` → sem N+1); `ExamRepository.list_pending`, `list_overdue(reference_date, sla_days, limit)`; `SuggestionRepository.create`, `set_status`; `AlertRepository.create_many`, `list(limit, offset) -> (rows, total)`; `AuditRepository.append`, `list(trace_id, limit, offset)`; `DEFAULT_PAGE_LIMIT = 20`, `MAX_PAGE_LIMIT = 100`.
- [ ] **4.6 — `records_adapter.py`:** `SqlPatientRecords(PatientRecordsPort)` converte ORM → schemas aplicando a minimização (P-043); `PatientNotFound` (`AST-404`).
- [ ] **4.7 — Seeds:** `SEED_SCENARIOS` rotulados (≥ 30 pacientes `PAC-001…`): exame atrasado; BI-RADS 4 sem conduta; BI-RADS 2 em dia; SOP com espironolactona + potássio; tamoxifeno + fluoxetina; sem pendências. `export_sql()`. **Os rótulos viram o gabarito dos fluxos na F8 e na F10.**. O comando `python -m app.db.seed` é idempotente e roda uma vez por ambiente, não a cada startup.
- [ ] **4.8 — Bootstrap:** `init_assistant_resources()` passa a chamar `init_records_db()` (só confere a conexão; com o banco fora do ar, o assistente responde 503 em vez de derrubar o backend).

## Critérios de aceite

`get_snapshot` com número fixo de queries (≤ 4) independentemente do número de exames; listagens paginadas com `total`; seeds reproduzíveis; `SqlPatientRecords` passa no teste de contrato; sugestões, alertas e auditoria persistem depois de recriar o backend; o papel da aplicação não alcança nada fora das suas tabelas.

## Audit

(1) contagem de queries igual com 1 e com 50 exames; (2) `PAC-999` → `PatientNotFound`; (3) `limit` ausente → 20, `limit=1000` → 100; (4) `"PAC-001'; DROP TABLE patients;--"` tratado como literal; (5) `alembic downgrade base` e `upgrade head` sem erro; (6) recriar o backend mantém sugestões e auditoria; (7) o papel `healthai_app` não consegue criar tabelas nem alterar o esquema.

## Commits

`feat(assistant): define port e schemas do prontuario` · `feat(db): cria schema e migracao inicial de prontuarios` · `feat(repositories): adiciona repositorios paginados sem n+1` · `feat(repositories): adapta prontuario ao port com minimizacao (P-043)` · `chore(db): adiciona seeds sinteticos rotulados` · `feat(db): habilita rls e papeis de menor privilegio no supabase`

## Entrega para a F5

`AuditRepository` (persistência da auditoria). **Para a F7/F8:** `SqlPatientRecords` e `SEED_SCENARIOS`.
