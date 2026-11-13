# F7 — Assistente Médico com LangChain (R2.1–R2.3, R3.1–R3.3, E2)

> [Índice](INDEX.md) · Anterior: [← F6](F06-rag-fontes.md) · Próxima: [F8 →](F08-fluxos-langgraph.md)  
> Referências: [Contexto e decisões](00-contexto-e-decisoes.md) · [Modelo de execução](00-modelo-de-execucao.md)  
> **Status:** ⏳ Não iniciada

## Objetivo

Montar o pipeline LangChain que integra a LLM fine-tuned (F3), o prontuário (F4), os guardrails e a auditoria (F5) e o RAG (F6), produzindo respostas contextualizadas, citadas e auditadas.

## Ponto de partida
- **Projeto:** a cadeia de fallback de `clinical_llm.py` e `logistics_llm._invoke_llm_with_fallback()` como referência de comportamento (**não refatorados**; consolidar no novo provider fica como refatoração futura); `CLINICAL_SYSTEM_PROMPT` (tom, saída em pt-BR); `shared_llm_cache` (só perguntas **sem** paciente).
- **Fases anteriores:** serviço `healthai-llm` (`llama-swap` + `llama-server` com os finalistas em CPU no Cloud Run) e **registro de modelos** (`ModelRegistry`, F3); `SqlPatientRecords` + seeds (F4); `InputGuard`, `OutputGuard`, `AuditLogger`, `AssistantAnswer` (F5); `ProtocolRetriever`, `format_protocol_context` (F6).
- **Seleção de modelo:** o assistente segue a ideia do `InferenceService._get_active_model()` (ler a escolha a cada uso), mas **não** o armazenamento: o `weights/active_models.json` fica no disco efêmero do Cloud Run e voltaria ao padrão a cada cold start. A escolha do assistente fica num objeto no Cloud Storage (`ActiveModelStore`, ver [scorecard de modelos](00-scorecard-modelos.md)).

## Etapas e agentes
- **Etapas ativas:** 2 (prompts e estratégia de citação), 3, 4 (com segurança e LGPD). Sem checkpoint (ADRs 002/003 já cobrem provider e acesso a dados).
- **Acionados:**

| Agente | Papel nesta fase |
| :--- | :--- |
| `ai-specialist` | Dono: prompts, cadeia LCEL, saída estruturada, citações, drafter de sugestão de conduta |
| `tester` (×2) | Provider + tools / chains + service (com `FakeListChatModel` e banco seed) |
| `developer` (×2) | Provider + service / tools |
| `security` | Auditoria das tools (sem SQL livre, sem abuso de tool), do prompt e do contexto (Etapa 4) |
| `privacy-officer` | Auditoria do contexto do paciente que vai ao LLM (P-043) e do cache, com veto |
| `reviewer` | Quality Gate |

- **Não acionados:** `architect` (decisões já nos ADRs 002/003), `dba` (o schema não muda), `designer`/`ux-reviewer` (sem UI nesta fase), `devops`.

## Execução em rodadas

| Rodada | Agente (paralelo) | Tarefas | Arquivos exclusivos |
| :--- | :--- | :--- | :--- |
| **R1** (Etapa 2) | `ai-specialist` | 7.3 (prompts) + formato de rotulagem do contexto para citação + `DraftAnswer` + ports `ChatModelProviderPort`/`CareSuggestionDrafterPort` | `app/assistant/prompts/*`, adendo em `ports.py`/`schemas/answer.py` |
| **R2** (TDD) | `tester#1` | Provider (resolução do modelo ativo pelo registro e pela escolha persistida no `ActiveModelStore` (Cloud Storage simulado), cache curto, recomendado/settings quando não há escolha, `is_available`, ID token do Cloud Run com `fetch_id_token` mockado, fallback auditado, `last_model_used`, aquecimento no startup sem bloquear a inicialização, aquecimento idempotente e aquecimento após troca do ativo) e tools (schema dos args, minimização, sem SQL) | `tests/assistant/llm/*`, `tests/assistant/tools/*` |
| | `tester#2` | Chain (citações ligadas aos ids recuperados; sem base → resposta padrão), drafter, service (guards sempre chamados; "dados atuais" com o banco seed) | `tests/assistant/chains/*`, `tests/services/test_assistant_service.py` |
| **R3** (código) | `developer#1` | 7.1 + 7.7 | `app/assistant/llm/{provider,active_model,active_model_store,cloud_run_auth,warmup}.py` |
| | `developer#2` | 7.2 | `app/assistant/tools/patient_tools.py` |
| | `ai-specialist` | 7.4, 7.5 | `app/assistant/chains/*` |
| **R4** (integração) | `developer#1` | 7.6 + bootstrap | `app/services/assistant_service.py`, `bootstrap.py` |
| **R5** (Etapa 4) | `security` ∥ `privacy-officer` ∥ `reviewer` ∥ `tester` | Tools/prompt ∥ contexto do paciente (**veto**) ∥ revisão ∥ suíte + Auto-Healer + 5 testes `llm_live` contra o `healthai-llm` publicado na F3 (e contra o Gemini, para o fallback) | — |
| **R6** (Fechamento) | `ai-specialist` ∥ Orquestrador | Seção E6 + diagrama da cadeia LCEL ∥ merge + `STATE.md` | `docs/fase3/secoes/05-assistente.md`, `docs/fase3/diagramas/clinical_qa_chain.mmd` |

## Código passo a passo
- [ ] **7.1 — `llm/active_model.py` + `llm/provider.py`:** `ActiveModelStore` (`get()`/`set()` sobre `settings.active_model_store_uri`: objeto no Cloud Storage em produção, arquivo local em dev; escrita com pré-condição de geração, para não sobrescrever uma troca concorrente) e `ActiveModelResolver(registry, store, settings).resolve() -> ModelCandidate` (cache de ~60 s, sem reiniciar o servidor); sem escolha registrada, usa o recomendado do registro e, sem scorecards, o fine-tuned de `settings.assistant_default_candidate`. `is_available(candidate)` lê o registro e a lista de modelos publicada na configuração do `healthai-llm` (gerada no deploy), **sem acordar o serviço**; para o Gemini, checa a chave (usado pelo painel na F9). `build_chat_model(candidate, settings)` monta `ChatOpenAI(base_url=f"{settings.llm_service_url}/v1", model=candidate.serving_ref, api_key="unused")` (cliente do protocolo compatível do `llama-server`; **nenhuma chamada à OpenAI**) ou `ChatGoogleGenerativeAI` (temperatura 0.1) com `.with_fallbacks([...])` no Gemini (quando o ativo já é o Gemini, o fallback é um segundo modelo Gemini, no mesmo padrão do `clinical_llm.py`). A OpenAI não entra na cadeia do assistente (sem crédito). **Autenticação no `healthai-llm`:** `CloudRunIdTokenProvider` (`google.oauth2.id_token.fetch_id_token`, audience = URL do serviço, cache até 5 min antes de expirar) injeta `Authorization: Bearer <id_token>` via `http_client=httpx.Client(auth=CloudRunIdTokenAuth(...))` no cliente e no `is_available`, quando `llm_auth_mode = cloud_run_id_token`. O Gemini só entra como contingência e **só para perguntas sem `patient_code`** e sem PII detectada pelo `pii_masker` no texto (P-051); com paciente e o fine-tuned fora do ar → `AssistantUnavailable` (`AST-021`, 503), sem enviar dados clínicos à API gratuita. `ModelUsageCallback(BaseCallbackHandler)` registra o modelo efetivo (`LLM_CALL`/`LLM_FALLBACK`, com `candidate_id`). `ChatModelProvider.last_model_used()` (P-048).
- [ ] **7.2 — `tools/patient_tools.py`:** `build_patient_tools(records, retriever, audit) -> list[StructuredTool]` com `args_schema` (`patient_code` com regex `^PAC-\d{3,}$`): `get_patient_snapshot`, `list_pending_exams`, `get_active_medications`, `search_protocols`. Cada tool registra `TOOL_CALL` e devolve só schemas minimizados. Nenhuma aceita SQL ou filtro livre (D6).
- [ ] **7.3 — Prompts:** `system_clinical.md` (inglês conciso, saída em pt-BR, apoio à decisão, P-040/041/042, "use somente o contexto rotulado e cite os ids"); `care_suggestion.md`; `prompt_loader.load_prompt(name) -> ChatPromptTemplate` com `{protocol_context}`, `{patient_context}`, `{question}` e `MessagesPlaceholder("history")`.
- [ ] **7.4 — `chains/clinical_qa_chain.py`:** `build_clinical_qa_chain(deps)`: `RunnableParallel(protocols=retrieve_step, patient=snapshot_step, question=…)` → `format_step` (contexto do paciente rotulado, ex.: `[patient_record:pending_exams[0]]`) → prompt → `model.with_structured_output(DraftAnswer)` (fallback `PydanticOutputParser` para modelos sem tool calling) → `attach_citations(draft, chunks, snapshot)` → `AssistantAnswer`. O modo determinístico (contexto injetado) é o padrão; o modo agente com tool calling fica opcional, atrás de flag.
- [ ] **7.5 — `chains/care_suggestion_chain.py`:** `CareSuggestionDrafter.draft(snapshot, chunks) -> SuggestionDraft` (sempre `requires_human_validation=True`), **usado pela F8**.
- [ ] **7.6 — `services/assistant_service.py`:** `AssistantService.ask(cmd: AskCommand{question, patient_code?, session_id, actor}) -> AssistantAnswer`: `new_trace_id` → `InputGuard` → chain → `OutputGuard` → auditoria. Memória curta por `session_id` (`RunnableWithMessageHistory`, TTL, no máximo N turnos). `init_assistant_service()` no bootstrap; chamadas ao LLM com `ainvoke` (assíncronas), para não prender threads do servidor enquanto o modelo gera; se o `LLMWarmupService` não estiver `READY`, levanta `ModelLoading` (`AST-022`, 503 com `Retry-After`) **na hora**, sem esperar a carga (limite de 60 s do Firebase Hosting, D16).
- [ ] **7.7 — `llm/warmup.py` (aquecimento automático, **P-052**):** `LLMWarmupService` com estado por modelo (`COLD` → `LOADING` → `READY` | `FAILED`) e `asyncio.Lock` (no máximo um carregamento em andamento). `trigger(candidate)` envia ao `healthai-llm` uma requisição mínima com `model = candidate.serving_ref` (`max_tokens=1`, timeout longo); o `llama-swap` carrega o modelo, e a resposta marca `READY`. `init_assistant_resources()` chama `trigger(ActiveModelResolver.resolve())` via `asyncio.create_task`, **sem bloquear o startup**: a requisição sai durante a inicialização do backend (com CPU disponível), e o carregamento acontece no `healthai-llm`, que tem CPU enquanto atende essa requisição. Assim, **o modelo escolhido no painel acorda junto com o cold start do sistema**, sem ação manual. O estado `READY` expira após `LLM_IDLE_TTL` (~10 min, abaixo do tempo em que o Cloud Run desliga a instância ociosa) e volta a `COLD`; assim o `model-status` (F9) dispara de novo o aquecimento quando o médico volta depois de um tempo parado. `status()` expõe o estado para a F9. Evento de auditoria `LLM_WARMUP` com modelo, duração e resultado. Se o ativo for o Gemini (contingência), não há aquecimento.

## Critérios de aceite

Toda resposta é um `AssistantAnswer` com `citations` e `patient_data_used`; fallback auditado; nenhuma tool devolve nome/CPF; alterar um exame no banco muda a próxima resposta; trocar a escolha no `ActiveModelStore` muda o modelo das próximas respostas sem reiniciar o servidor e **sobrevive a um cold start**; ao subir, o backend dispara o carregamento do modelo ativo sem atrasar a própria inicialização (P-052).

## Audit

(1) "A paciente PAC-007 tem exames pendentes? O que o protocolo recomenda?" → cita o exame (`patient_record`) e o protocolo (documento + página); (2) pergunta sem suporte → resposta padrão com `citations=[]`; (3) "Prescreva o tratamento" → sugestão com `requires_human_validation=true`; (4) serviço do fine-tuned fora → pergunta geral responde via Gemini com `model="gemini-…"` e `LLM_FALLBACK`; pergunta com `patient_code` (ou com PII no texto) → 503 `AST-021`, sem chamar o Gemini; (5) escolha alterada no `ActiveModelStore` → `meta.model` muda nas chamadas seguintes, e recriar o backend (simula um cold start) mantém a escolha; candidato ativo indisponível → fallback com `LLM_FALLBACK`; (6) com `llm_auth_mode = cloud_run_id_token`, toda chamada aos serviços de LLM leva o ID token, renovado antes de expirar; (7) cold start do backend com o `healthai-llm` simulado lento → a inicialização termina sem esperar, o carregamento é pedido uma única vez e o estado chega a `READY`.

## Commits

`feat(assistant): adiciona provider de llm com fallback auditado (P-048)` · `feat(assistant): adiciona tools parametrizadas de prontuario (P-043)` · `feat(assistant): cria cadeia lcel de qa clinico com citacoes (P-041)` · `feat(assistant): cria drafter de sugestao de conduta (P-040)` · `feat(assistant): adiciona servico do assistente com guardrails` · `feat(assistant): resolve o modelo ativo do assistente pelo registro` · `feat(assistant): aquece o modelo ativo junto com o cold start do sistema (P-052)`

## Entrega para a F8/F9

`AssistantService`, `CareSuggestionDrafter`, `ChatModelProvider`.
