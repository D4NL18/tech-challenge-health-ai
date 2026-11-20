# Fase 3 — Custos e FinOps: até R$5/mês no projeto inteiro (D14)

> [Índice do plano](INDEX.md) · [Contexto e decisões](00-contexto-e-decisoes.md) · [Modelo de execução](00-modelo-de-execucao.md) · [Scorecard de modelos](00-scorecard-modelos.md)

## Restrição

O projeto inteiro (Fases 1, 2 e 3: backend, frontend, serviços de LLM, armazenamento, builds e treino) deve **caber no free tier** ou custar **no máximo R$5 por mês** (≈ US$0,90 ao câmbio de referência de ~R$5,50/US$; o câmbio exato fica no alerta de orçamento, na moeda da conta de faturamento). **Meta de custo esperado: R$0–2/mês**, deixando margem até o teto.

> [!IMPORTANT]
> Os limites de free tier abaixo são os de referência das páginas oficiais do Google Cloud. **Eles são conferidos na F0** (`devops`), e qualquer diferença atualiza este documento antes da F3. O free tier do Google Cloud vale **por conta de faturamento**: se a mesma conta tiver outros projetos, a cota é dividida.

## Princípios

1. **Nada fica ligado sem uso:** todo serviço Cloud Run com `min-instances 0` e cobrança por requisição (CPU só durante a requisição). Sem `min-instances`, sem CPU sempre alocada.
2. **Sem GPU na nuvem:** GPU no Cloud Run ou endpoints dedicados custam por hora e estourariam o teto em poucas horas. O treino roda no **computador pessoal** (GTX 1660 SUPER, sem custo de nuvem), e a produção serve modelos pequenos quantizados em **CPU**.
3. **Tetos explícitos:** `max-instances` baixo em todos os serviços, rate limit por usuário, endpoints do assistente só para usuários autenticados.
4. **Armazenamento enxuto:** política de limpeza no Artifact Registry, lifecycle no Cloud Storage e imagens pequenas.
5. **Medir, não supor:** alerta de orçamento, verificação mensal no billing e vCPU-s por resposta medidos na F3 e na F10.

## Inventário de serviços e custo esperado

| Serviço | Uso no projeto | Free tier de referência (confirmar na F0) | Uso estimado | Custo esperado |
| :--- | :--- | :--- | :--- | :--- |
| **Cloud Run** (backend + `healthai-llm`) | API FastAPI e serviços de LLM em CPU, cobrança por requisição | 180.000 vCPU-s, 360.000 GiB-s e 2 milhões de requisições por mês (região tier 1, ex.: us-central1); 1 GiB de saída na América do Norte | Ver o cálculo abaixo; uso acadêmico fica bem abaixo da cota | R$0 |
| **Artifact Registry** | Imagens do backend e do `llama-server` | 0,5 GB de armazenamento por mês | Backend (com PyTorch) é o maior item; `llama-server` CPU é pequeno | **Principal custo real:** ~US$0,10/GB-mês acima de 0,5 GB. Com limpeza (só as 2 versões mais recentes) e PyTorch CPU-only: ≈ R$0,50–1,50 |
| **Cloud Build** | Builds do `gcloud run deploy --source` e da imagem do LLM | Minutos de build gratuitos por mês (cota vigente a confirmar) | Poucos deploys por semana | R$0 |
| **Cloud Storage** | GGUF dos finalistas (`healthai-llm-models`) | 5 GB-mês Standard em us-central1/us-east1/us-west1 + operações gratuitas | ≤ ~4,5 GB (2–3 finalistas de 0,8–1,5 GB; os não finalistas ficam só no HF) | R$0 |
| **Cloud Storage** (configuração) | Escolha do modelo ativo (`active_models.json`, alguns bytes) | Mesma cota gratuita | 1 leitura por cold start + 1 escrita por troca | R$0 |
| **Supabase** (free) | Postgres do prontuário, auditoria, checkpoints e vetores (D15, D17) | 500 MB de banco; pausa após 7 dias sem uso | < 50 MB; keep-alive semanal pelo GitHub Actions | R$0 |
| **Cloud Logging** | Logs JSON do backend e dos serviços | 50 GiB de ingestão por projeto por mês | Muito abaixo (nível INFO, sem payloads) | R$0 |
| **Firebase Hosting** (cota gratuita; o projeto já tem faturamento por causa do Cloud Run) | Frontend Angular e rewrite `/api/**` para o Cloud Run (D16) | 10 GB de armazenamento, 360 MB/dia de transferência | Bundle de poucos MB | R$0 |
| **Gemini API** (free tier) | Fallback de contingência sem dados de paciente, geração de dados sintéticos (F1) e juiz da avaliação (F10) | Gratuito com limite de requisições por minuto e por dia | Dentro dos limites com cache, backoff e geração espalhada em dias | R$0 |
| **Computador pessoal** | Treino, HPO e bateria pesada da avaliação (F10) | — | ~8–12 h de GPU por candidato | R$0 de nuvem |
| **Kaggle Notebooks** (contingência) | Só se a GPU local falhar ou para paralelizar o segundo candidato | ~30 h de GPU por semana | Opcional | R$0 |
| **Hugging Face Hub** | Adapters, model cards, cópia dos GGUF | Repositórios gratuitos | — | R$0 |
| **GitHub Actions** | CI e deploy | Minutos gratuitos (ilimitados em repositório público) | — | R$0 |
| **Cloud Billing — budgets** | Alerta de orçamento | Gratuito | — | R$0 |
| **Total esperado** | | | | **≈ R$0,50–1,50/mês** (teto R$5) |

> **Fora do plano por custo:** GPU no Cloud Run, Vertex AI endpoints, HF Inference Endpoints pagos, Cloud SQL, Memorystore, `min-instances ≥ 1`, CPU sempre alocada, IPs estáticos, load balancer, VPC connector.

## Perfil de uso e orçamento do Cloud Run

**Premissas para a estimativa:** cerca de **5 h por mês** de uso ativo em produção (demonstrações, testes, gravação do vídeo e a medição de latência da F10). É uma **estimativa para calcular o custo, não um limite**: nada no sistema bloqueia o uso acima disso. **Cold start aceito** (sem instâncias mínimas; o aquecimento automático do P-052 só carrega o modelo quando o sistema acorda).

| Serviço | Recursos | Tempo ativo no mês (estimado) | Consumo | Uso do free tier (180 mil vCPU-s · 360 mil GiB-s) |
| :--- | :--- | :--- | :--- | :--- |
| `healthai-llm` | 4 vCPU / 4 GiB | 5 h = 18.000 s, incluindo cold starts, trocas de modelo e aquecimentos automáticos | 72.000 vCPU-s · 72.000 GiB-s | 40% · 20% |
| Backend | 1 vCPU / 2 GiB | 5 h = 18.000 s | 18.000 vCPU-s · 36.000 GiB-s | 10% · 10% |
| **Total** | | | **90.000 vCPU-s · 108.000 GiB-s** | **50% · 30%** |

- **Margem:** o free tier comporta até ~10 h/mês nesse perfil, o dobro da estimativa. Acima disso, cada hora extra de um serviço de LLM custa, a preço de lista de referência (≈ US$0,000024 por vCPU-s e US$0,0000025 por GiB-s), cerca de **US$0,38 ≈ R$2,10**. Por isso há `max-instances 1`, autenticação obrigatória e alerta de orçamento.
- **Requisições:** muito abaixo dos 2 milhões gratuitos.
- **Aquecimento automático (P-052):** cada cold start do sistema também carrega o modelo ativo (~120–240 vCPU-s). Mesmo com 100 cold starts por mês, isso dá ≈ 24 mil vCPU-s (≈ 13% do free tier), coberto pela margem.
- **Medição:** a F3 (R8) e a F10 medem o vCPU-s por resposta e o tempo de cold start reais e atualizam esta tabela.
- **Avaliação:** a bateria pesada da F10 roda no computador local, com a mesma imagem do `llama-server` e os mesmos GGUF. No Cloud Run, só as 50 perguntas de latência por candidato (≈ 50 min de uso).

## Guardrails de custo (implementados na F0 e conferidos em toda fase)

| Guardrail | Onde | Fase |
| :--- | :--- | :--- |
| Alerta de orçamento de **R$5/mês** com avisos em 50%, 90% e 100% (real e previsto), por e-mail | Cloud Billing | F0 |
| **Política de limpeza do Artifact Registry**: manter só as 2 versões mais recentes de cada imagem (o `--source` do Cloud Run acumula uma imagem por deploy); só regra de "manter as N mais recentes", **nunca exclusão por idade**, porque a imagem da revisão em produção precisa continuar existindo para novas instâncias subirem | Artifact Registry | F0 |
| **Backend com PyTorch CPU-only** (`--index-url` das wheels CPU) para reduzir a imagem em GBs | `backend/requirements.txt` / `Dockerfile` | F0 |
| Lifecycle no bucket `healthai-llm-models`: apagar versões não correntes dos GGUF | Cloud Storage | F0 |
| `min-instances 0` e `max-instances` ≤ 2 em todos os serviços; `healthai-llm` com `max-instances 1` e `concurrency 4` (requisições simultâneas esperam na fila do `llama-server`, que atende uma por vez, em vez de receberem 429 do Cloud Run) | Cloud Run | F0 (backend), F3 (LLM) |
| Rate limit do assistente por usuário (10/min) além do limiter global | Backend | F9 |
| Endpoints do assistente só para `MEDICO` autenticado (sem tráfego anônimo acordando o LLM) | Backend | F9 |
| Disponibilidade dos finalistas no painel lida do registro e da configuração publicada (o painel não acorda o `healthai-llm`); aquecimento idempotente, no máximo um carregamento por vez | Backend | F7, F9 |
| Logs em nível INFO, sem payloads; filtro de exclusão para logs de health check | Cloud Logging | F5, F11 |
| Verificação de custo no fechamento das fases F3, F10 e F11 | Billing | F3, F10, F11 |

## Privacidade × free tier do Gemini

No free tier da Gemini API, o conteúdo enviado pode ser usado pelo Google para melhorar produtos. Por isso:
- **Dados sintéticos e anonimizados** (geração da F1, juiz da F10): permitido.
- **Contexto de paciente em produção:** **nunca vai para o Gemini gratuito**. Se o fine-tuned estiver fora do ar, perguntas com `patient_code` recebem 503 (`AST-021`); só perguntas gerais (sem `patient_code` e sem PII detectada pelo `pii_masker` no texto) podem cair no fallback Gemini (P-051).
- O RIPD (F0) registra essa regra. Funcionalidades das Fases 1 e 2 que já enviam dados ao Gemini ficam **fora do escopo** desta fase, registradas como dívida para o `privacy-officer`.

## Responsabilidades por fase

| Fase | Ação de custo |
| :--- | :--- |
| [F0](F00-fundacao.md) | `devops`: conferir free tiers vigentes, criar o alerta de R$5, limpeza do Artifact Registry, PyTorch CPU-only, bucket com lifecycle, `max-instances`; ADR-010 (D14) |
| [F1](F01-corpus.md) | Geração sintética no free tier do Gemini, com cache e geração espalhada em dias |
| [F3](F03-fine-tuning-qlora.md) | Treino no computador pessoal; serviços de LLM em CPU com escala a zero; medição de vCPU-s por resposta; conferência do billing |
| [F9](F09-api-auth-interface.md) | Rate limit, autenticação obrigatória e disponibilidade lida do registro (sem acordar o `healthai-llm`) |
| [F10](F10-avaliacao.md) | Bateria pesada no computador local; só latência no Cloud Run; métrica de custo no scorecard e gate de orçamento |
| [F11](F11-documentacao-release.md) | Revisão final de custo, seção de custos no README e no relatório |