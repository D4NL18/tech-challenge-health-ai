# F3 — Pipeline de Fine-tuning QLoRA, Otimização de Hiperparâmetros e Publicação do Modelo (R1.1–R1.3, E1, E5)

> [Índice](INDEX.md) · Anterior: [← F2](F02-anonimizacao-curadoria.md) · Próxima: [F4 →](F04-prontuario.md)  
> Referências: [Contexto e decisões](00-contexto-e-decisoes.md) · [Modelo de execução](00-modelo-de-execucao.md) · [Custos e FinOps](00-custos-finops.md)  
> **Status:** ⏳ Não iniciada

## Objetivo

Fazer a **triagem de 5 modelos base** (D1) e treinar os **2–3 finalistas** com QLoRA no **computador pessoal (GTX 1660 SUPER 6 GB, i5-11400, 32 GB RAM, WSL2 Ubuntu)**, usando a melhor configuração de hiperparâmetros encontrada para cada um dentro de um orçamento de horas de máquina; registrar todos os experimentos de forma reproduzível; publicar os fine-tuned **em produção** num **serviço único `healthai-llm`** em CPU, **dentro do free tier**, que mantém em memória só o modelo ativo e carrega os outros sob demanda; e **registrar cada candidato no registro de modelos**, que alimenta o scorecard (F10) e a escolha no painel admin (F9).

## Pré-condição

Pool de triagem e regra de finalistas (**D1**) e scorecard pré-registrado (**D13**) aprovados na F0 ([scorecard de modelos](00-scorecard-modelos.md)); **D3** (treino local no computador pessoal), **D4** (serving em CPU no Cloud Run) e **D14** (orçamento ≤ R$5/mês, [custos e FinOps](00-custos-finops.md)) registrados. A D12 (estratégia de HPO, abaixo) é registrada no ADR-001.

## Ponto de partida
- **Projeto:** o padrão de `training_scripts/` (CLI offline, métricas JSON + PNG em `weights/`) e `visualizer.py` (estilo dos gráficos). Os artefatos vão para `weights/llm/` e **não** para `weights/metrics/`, porque o `/admin/metrics` interpreta o nome `metricas_<modelo>_<doença>.json` e quebraria.
- **Otimização da Fase 2:** `app/genetic/hyperopt/` (AG com população 40 × 20 gerações ≈ 800 avaliações por modelo, fitness F2). Funciona bem para os modelos tabulares, em que cada avaliação leva segundos. **Não é reaproveitado aqui**, porque cada avaliação de uma LLM é um treino de minutos em GPU, e a GPU local é modesta (justificativa na estratégia abaixo). O relatório da Fase 3 registra esse contraste entre as duas fases.
- **Hardware de treino:** computador pessoal (GTX 1660 SUPER 6 GB, i5-11400, 32 GB RAM, WSL2 Ubuntu), verificado neste planejamento. GPU Turing **sem tensor cores e sem bf16**, com 6 GB de VRAM: suficiente para QLoRA 4-bit em modelos de 1B–1,5B com batch pequeno e gradient checkpointing. O ambiente (CUDA no WSL2, bitsandbytes, Unsloth) é validado já na F0 (passo 0.9).
- **Fases anteriores:** `processed/{train,val,test}.jsonl` em `messages` (F2); `requirements-training.txt` com `optuna` (F0); bucket `healthai-llm-models` no Cloud Storage e alerta de orçamento (F0); ADR-001 + D1/D3/D4/D12/D14; ADR-009 + `model_scorecard.yaml` (D13, F0).

## Estratégia de otimização de hiperparâmetros (D12)

### Por que não AG nem grid manual

| Estratégia | Treinos necessários (ordem de grandeza) | Usa o histórico? | Corta treinos ruins cedo? | Veredito para LLM |
| :--- | :--- | :-: | :-: | :--- |
| Grid manual (ex.: 4 `r` × 4 `lr` × 2 módulos × 2 dropout) | 64 treinos completos | ✗ | ✗ | Caro e cego; cresce exponencialmente com cada parâmetro |
| Poucos treinos manuais (2–3) | 2–3 | Só a intuição | ✗ | Barato, mas quase certamente subótimo e sem evidência para o relatório |
| Random search | 30–60 | ✗ | ✗ | Melhor que grid, mas desperdiça GPU em regiões ruins |
| Algoritmo Genético (módulo da Fase 2) | 40 × 20 = 800 avaliações | ✓ | ✗ | Inviável: cada avaliação é um treino de LLM |
| Otimização Bayesiana (Optuna TPE) | 20–30 | ✓ | ✗ | Boa, mas cada tentativa ainda roda até o fim |
| **TPE + poda multifidelidade (Hyperband/ASHA) + warm start** ✅ | **~16 tentativas curtas por candidato, a maioria podada cedo + 4 treinos completos** | ✓ | ✓ | **Escolhida:** concentra as horas da GPU local nas configurações promissoras |

### Como funciona
1. **Warm start:** as primeiras tentativas são configurações conhecidas e boas da literatura de QLoRA (`study.enqueue_trial`), começando pelo padrão `r=16`, `alpha=32`, `lr=2e-4`, `all-linear`. A busca já parte de uma região boa, e o padrão vira a linha de base para medir o ganho da otimização.
2. **Estágio 1 — busca em baixa fidelidade (proxy):** cada tentativa treina em ~25% do `train` (estratificado por `task_type`), com `max_seq_length` reduzido e no máximo `HPO_MAX_STEPS` passos (ex.: 300). A cada `HPO_EVAL_STEPS` (ex.: 50) passos, o `eval_loss` é medido num **subconjunto fixo de 200 exemplos do `val`** e reportado ao Optuna. O `HyperbandPruner` encerra cedo as tentativas que estão piores que as demais no mesmo ponto do treino. O `TPESampler(multivariate=True)` usa o histórico para propor as próximas configurações.
3. **Estágio 2 — confirmação em fidelidade total:** o **top-3 do estágio 1 + a configuração padrão do warm start** treinam com 100% dos dados, `max_seq_length` completo e early stopping no `val`. A escolha final usa um **score composto** medido no **restante do `val`** (exemplos que a busca nunca viu, o que evita sobreajustar a seleção):
   - `eval_loss` normalizado (peso 0.4);
   - acurácia em 100 perguntas PubMedQA do `val` (peso 0.3);
   - conformidade de formato em 50 laudos/receitas do `val`: campos obrigatórios e aviso de validação (peso 0.3);
   - **restrição eliminatória:** qualquer prescrição direta sem a marca de validação (P-040) desclassifica a configuração.
   Em empate técnico (diferença < 1%), vence o menor `r`, porque é mais barato de servir.
4. **O `test` congelado da F2 não é usado em nenhum momento da busca.** Ele só aparece na F10.

### Espaço de busca
| Hiperparâmetro | Faixa | Por quê |
| :--- | :--- | :--- |
| `learning_rate` | log-uniforme [5e-5, 5e-4] | O mais sensível em LoRA; varia em ordens de grandeza |
| `lora_r` | {8, 16, 32, 64} | Capacidade do adapter vs. custo e risco de sobreajuste |
| `lora_alpha_ratio` | {1, 2} → `alpha = r × ratio` | Mantém a escala do LoRA coerente com o rank e reduz uma dimensão livre |
| `use_rslora` | {False, True} | Rank-stabilized LoRA estabiliza ranks altos |
| `lora_dropout` | {0.0, 0.05, 0.1} | Regularização num dataset pequeno |
| `target_modules` | {`attn` (q,k,v,o), `all-linear`} | Onde o adapter atua (qualidade vs. memória) |
| `warmup_ratio` | uniforme [0.0, 0.1] | Estabilidade do início do treino |
| `lr_scheduler_type` | {`cosine`, `linear`} | Decaimento da taxa de aprendizado |
| `weight_decay` | {0.0, 0.01} | Regularização |
| `neftune_noise_alpha` | {0 (desligado), 5} | Ruído em embeddings, que costuma melhorar instruction tuning (suportado pelo TRL) |

**Fixos (não buscados, decididos pelo hardware ou pelos dados):** batch por dispositivo = o maior que cabe nos 6 GB (tipicamente 1–2 com gradient checkpointing); `gradient_accumulation` para batch efetivo 16; `max_seq_length` = p95 dos tokens do dataset, limitado a 1024 pela VRAM (512 no proxy); NF4 + double quant; fp16 (a GTX 1660 SUPER não tem bf16); se aparecer NaN ou instabilidade em fp16, problema conhecido na série GTX 16xx, o `compute_dtype` do 4-bit passa para fp32 (mais lento, mas estável); épocas controladas por early stopping no estágio 2; seed fixa.

### Otimizações de engenharia (menos tempo de GPU local por tentativa)
- **Dataset pré-tokenizado uma única vez** (`save_to_disk`) e compartilhado entre as tentativas.
- **Modelo base quantizado carregado uma vez por sessão.** Cada tentativa cria um adapter novo e o remove no fim (`delete_adapter`), com limpeza de memória (`gc.collect()`, `torch.cuda.empty_cache()`). Se a memória fragmentar, há fallback para recarregar o modelo.
- **Packing de sequências** no `SFTTrainer` e **gradient checkpointing**.
- **Estudo persistente e retomável:** `optuna` com storage SQLite local (`weights/llm/hpo/<candidate_id>/optuna.db`, fora do git), `load_if_exists=True` e `RetryFailedTrialCallback`. Se o treino for interrompido (queda de energia, reinício, uso do computador), a busca continua de onde parou.
- **Orçamento explícito em horas de máquina:** `HPO_N_TRIALS` (ex.: 16 por candidato) **e** `HPO_TIMEOUT_HOURS`, o que acontecer primeiro. A meta é **~8–12 h por candidato**, rodando de preferência à noite. Os valores finais são calibrados pelo **tempo por passo medido no primeiro treino** (rodada R4).
- **Recomendado: Unsloth** como backend de QLoRA (acelera e economiza memória, o que importa com 6 GB de VRAM; roda no WSL2 Ubuntu), se compatível com os candidatos da D1, atrás de uma flag. Sem compatibilidade, usa `transformers` + `peft` puro.

### Saídas para o relatório (E5)
`weights/llm/hpo/<candidate_id>/trials.csv` (todas as tentativas, parâmetros, estado podada/completa e valores intermediários), `best_params.json`, `stage2_comparison.json` e gráficos PNG com `optuna.visualization.matplotlib`: histórico da otimização, importância dos hiperparâmetros (fANOVA), coordenadas paralelas e curvas intermediárias mostrando as podas.

## Triagem de modelos base (estágio 0, D1)

Antes da busca de hiperparâmetros, cada modelo do pool passa por um teste barato. Só os melhores seguem para a HPO completa, o que mantém o tempo de GPU local sob controle.

| `candidate_id` | Modelo (id no HF conferido na F0) | Licença | Observação |
| :--- | :--- | :--- | :--- |
| `llama32-1b` | `meta-llama/Llama-3.2-1B-Instruct` | Llama (pedir acesso no HF) | Família citada no PDF; o mais rápido |
| `qwen25-1_5b` | `Qwen/Qwen2.5-1.5B-Instruct` | Apache-2.0 | Bom em multilíngue para o tamanho |
| `qwen3-1_7b` | `Qwen/Qwen3-1.7B` | Apache-2.0 | Provavelmente o mais forte da faixa; **modo thinking desligado** (`enable_thinking=False` no template) por latência e formato |
| `gemma3-1b` | `google/gemma-3-1b-it` | Gemma (aceitar os termos no HF) | Leve e moderno; o português precisa ser conferido |
| `tucano-2b4` | `TucanoBR/Tucano-2b4-Instruct` | Apache-2.0 | Treinado nativamente em português; o mais lento em CPU e menos testado em instruções |

- **Na F0**, a lista é conferida contra os modelos abertos mais recentes de 1–2,5B (pode haver geração mais nova) e aprovada no checkpoint, junto com a regra abaixo. Ela fica **pré-registrada** no ADR-001 e no `hpo_config.yaml`.
- **Procedimento por modelo** (um por vez na GPU local, ~30–60 min cada, ~3–5 h no total): QLoRA com a config padrão do warm start em baixa fidelidade (25% do `train`, 300 passos, sequência 512) → **o mesmo score composto do estágio 2**, medido no `val` de seleção (`eval_loss` normalizado, PubMedQA do `val`, conformidade de template) → restrição P-040. **Latência em CPU:** o GGUF Q4_K_M do modelo base, no `llama-server` local limitado a **4 threads** (imita os 4 vCPU do Cloud Run), com 20 perguntas fixas (p95 quente e tempo de carga), multiplicado pelo **fator de conversão local → Cloud Run** medido na F0 (0.9).
- **Regra dos finalistas:** exclui quem tiver latência p95 estimada para o Cloud Run acima de 45 s (folga para o limite de 60 s do Firebase Hosting, D16) ou violar a P-040; ordena pelo score composto; **finalistas = os 2 primeiros, mais o 3º se estiver a até 2 pontos do 2º** (máximo de 3, por causa do tempo de treino e dos 5 GB gratuitos do Cloud Storage). O PDF aceita "LLaMA, Falcon ou outro", então não é obrigatório ter um LLaMA entre os finalistas.
- **Saídas:** `weights/llm/triage/triage_results.{json,csv,png}`. O tempo por passo e a memória medidos na triagem **calibram o orçamento da HPO** de cada finalista e mostram se o fp16 é estável.
- **Não finalistas:** entram no registro como `kind="reference"`, só com o resultado da triagem. Não são servidos, não vão para o bucket e não podem ser ativados. O resultado deles vai para o relatório (E5).

## Treino de múltiplos candidatos e registro de modelos (D1/D13)
- Cada **finalista** da triagem tem **o seu próprio estudo do Optuna** (`study_name = hpo-<candidate_id>`), porque hiperparâmetros não transferem entre arquiteturas.
- **Execução dos candidatos:** com uma única GPU de 6 GB, os candidatos treinam **em sequência** (um estudo por vez). As tarefas de código, testes, export e registro continuam paralelas entre os agentes. **Opcional:** rodar o segundo candidato no Kaggle gratuito ao mesmo tempo, se for preciso encurtar o prazo.
- Por candidato, o estágio 2 produz o **FT otimizado** (selecionável no painel) e o **FT com a config padrão** (referência para medir o ganho da HPO). O modelo base sem fine-tuning também entra como referência.
- **Export:** cada FT otimizado vira um GGUF Q4_K_M enviado ao bucket `healthai-llm-models` (Cloud Storage, dentro dos 5 GB gratuitos) e ao HF Hub (cópia e entregável público do E1).
- **Registro:** `weights/llm/registry/<candidate_id>.json` para os finalistas (FT otimizado, FT padrão e base), para os não finalistas (só a triagem) e para a referência Gemini, com identidade, origem, hiperparâmetros, artefatos e `scorecard: null` (status "aguardando avaliação"). O scorecard só é calculado na F10, com o `test` congelado.
- O score composto do estágio 2 escolhe o **vencedor da HPO dentro de cada candidato**, usando o `val`. A escolha **entre candidatos** não acontece aqui: ela vem do scorecard (F10) e da decisão do admin no painel (F9).

## Publicação em produção (serviço único `healthai-llm`, troca sob demanda)

O objetivo da tarefa é ter o fine-tuned respondendo em produção (P-051), **sem passar de R$5/mês** (D14). Por isso não há GPU na nuvem: os finalistas são pequenos (1–2,5B) e quantizados em Q4, o que torna viável servir em CPU. Um **único serviço** mantém em memória só o modelo escolhido no painel; os outros finalistas ficam guardados e só são carregados quando o admin troca para eles.

| Aspecto | Decisão |
| :--- | :--- |
| Servidor | **`llama-swap`** (proxy, versão fixa) na frente do **`llama-server`** (llama.cpp, build CPU, versão fixa, **portátil**: variantes de CPU escolhidas em tempo de execução, sem `-march=native`, porque o Cloud Run pode alocar processadores diferentes do da máquina de build). O `llama-swap` sobe o `llama-server` com o modelo pedido no campo `model` da requisição e descarrega o anterior: **só o modelo ativo fica em memória**. API no protocolo compatível com o da OpenAI, usada só como formato (**nenhuma chamada à OpenAI**). Na F0 confere-se se o próprio `llama-server` já troca de modelo sozinho; se trocar, o `llama-swap` sai |
| Modelos publicados | Uma entrada de configuração por finalista (`healthai-med-<candidate_id>` → `/models/<candidate_id>.gguf`), gerada pelo `deploy-llm.yml` a partir do registro. Não finalistas não entram |
| Pesos | GGUF dos 2–3 finalistas no bucket `healthai-llm-models` (≤ ~4,5 GB, dentro dos 5 GB gratuitos, em us-central1), montado como **volume do Cloud Storage** somente leitura. A imagem não carrega pesos. Exige o ambiente de execução de 2ª geração e `roles/storage.objectViewer` para a service account do serviço; o R8 mede a carga pelo volume com e sem `--no-mmap` e fica com a mais rápida |
| Recursos | 4 vCPU / 4 GiB (dimensionado pelo maior finalista), `--concurrency 4` no Cloud Run com `--parallel 1` no servidor (requisições simultâneas, como o aquecimento e a primeira pergunta, esperam na fila do `llama-server` em vez de receberem 429 do Cloud Run), `--min-instances 0 --max-instances 1`, cobrança por requisição (CPU só durante a requisição), timeout de 300 s. Sem `min-instances` e sem CPU sempre alocada |
| Latência | Prompt de sistema fixo no início (o `llama-server` reaproveita o cache do prefixo entre requisições), contexto de RAG enxuto (k=3), `max_tokens` limitado e `--ctx-size` dimensionado para esse orçamento |
| Troca de modelo | Quando o admin ativa outro finalista no painel, o backend pede a carga dele; o `llama-swap` descarrega o atual e carrega o novo (dezenas de segundos), e o painel mostra "carregando" → "pronto" (F9) |
| Aquecimento automático (P-052) | Quando o sistema acorda de um cold start, o backend dispara **em paralelo** a carga do modelo ativo no `healthai-llm`, sem atrasar a própria inicialização. Quando o médico chega ao assistente, o modelo já está carregando ou pronto. Implementado na F7 (`LLMWarmupService`) |
| Custo | Estimativa com base em **~5 h de uso por mês** em produção (demo, testes, gravação e a medição de latência da F10); é só a base do cálculo, não um limite. 5 h em 4 vCPU / 4 GiB ≈ 72 mil vCPU-s e 72 mil GiB-s, cerca de 40% e 20% do free tier do Cloud Run (180 mil vCPU-s e 360 mil GiB-s, compartilhados com o backend; confirmar na F0). Detalhes em [custos e FinOps](00-custos-finops.md) |
| Acesso | `--no-allow-unauthenticated`; a service account do backend recebe `roles/run.invoker`; o backend envia **ID token** (audience = URL do serviço), implementado na F7 |
| Cold start | **Aceito**, e mitigado pelo aquecimento automático. Probe de startup no `/health` e aviso de "carregando o modelo" na UI. Sem `min-instances` |
| Deploy | `.github/workflows/deploy-llm.yml` (`workflow_dispatch` e mudanças em `llm_service/` ou no registro): build da imagem pequena, geração da configuração do `llama-swap` a partir do registro e `gcloud run deploy healthai-llm`. O serviço sobe **já na F3**; o backend de produção passa a usá-lo na F11 |
| Contingência | Gemini (free tier) só como fallback, e só para perguntas **sem dados de paciente** (P-051). Com contexto de paciente e o fine-tuned fora do ar, a resposta é 503 (`AST-021`), sem enviar dados clínicos a uma API gratuita |

## Etapas e agentes
- **Etapas ativas:** 2 (config de treino e desenho da HPO), 3, 4, 5 (MLOps: publicação no HF Hub, no Cloud Storage e nos serviços Cloud Run). Sem checkpoint (ADR-001/D12 aprovados na F0).
- **Acionados:**

| Agente | Papel nesta fase |
| :--- | :--- |
| `ai-specialist` | Dono: espaço de busca, warm start, fidelidades, score composto, condução dos estágios 1 e 2 **para cada candidato**, análise e escolha do vencedor de cada candidato |
| `tester` (×2) | Smoke de treino, export e registro / testes da HPO (amostragem, poda, retomada, score composto) |
| `developer` (×3) | Data module + treino / módulo de HPO / export para GGUF + upload + registro de modelos |
| `devops` | Ambiente de treino local (WSL2 Ubuntu + CUDA + bitsandbytes/Unsloth, validado na F0), scripts de execução, storage local do Optuna, HF Hub, bucket do Cloud Storage, artefatos fora do git; **imagem `llama-swap` + `llama-server` e deploy do serviço `healthai-llm`** dentro do free tier, workflow `deploy-llm.yml` |
| `security` | Auditoria do `healthai-llm`: sem acesso público, IAM `run.invoker` só para o backend, ID token, bucket privado com acesso só da service account dos serviços |
| `reviewer` | Quality Gate |

- **Não acionados:** `privacy-officer` (o dataset já foi auditado na F2; os serviços só recebem prompts já minimizados e pseudonimizados pelo backend), `dba`, `architect`, `designer`/`ux-reviewer`.

## Execução em rodadas

| Rodada | Agente (paralelo) | Tarefas | Arquivos exclusivos |
| :--- | :--- | :--- | :--- |
| **R1** (Etapa 2) | `ai-specialist` | 3.1 (config base) + especificação da HPO (espaço, warm start, fidelidades, orçamento em horas de máquina, score composto) | `finetuning/config/{qlora_config,hpo_config}.yaml`, `finetuning/config.py` |
| **R2** (TDD) | `tester#1` | Smoke (`--smoke` em modelo minúsculo), config inválida, adapter carregável, GGUF gerado e servido por um `llama-server` local, registro de modelos (schema válido, escrita idempotente, `scorecard` nulo até a F10) | `tests/finetuning/test_train_smoke.py`, `test_export.py`, `test_registry.py` |
| | `tester#2` | HPO: espaço gera configs válidas, `alpha = r × ratio`, callback poda quando o pruner manda, estudo retoma do storage, score composto e restrição P-040, **smoke de HPO** (2 tentativas × 4 passos no modelo minúsculo, sem GPU), regra da triagem (exclusão por latência e P-040, top-2 + 3º a até 2 pontos) | `tests/finetuning/test_hpo.py` |
| **R3** (código) | `developer#1` | 3.2, 3.3 | `finetuning/{data_module,train_qlora}.py` |
| | `developer#2` | 3.4 (módulo de HPO) + 3.4a (triagem) | `finetuning/hpo/*`, `finetuning/triage.py` |
| | `developer#3` | 3.7 (desenvolvido e testado com o modelo minúsculo) + 3.9 (registro de modelos) | `finetuning/merge_and_export.py`, `finetuning/register_candidates.py`, `app/assistant/llm/registry.py` |
| | `devops` | 3.5 | `finetuning/scripts/*` |
| **R4** (GPU local — triagem e calibração) | `ai-specialist` ∥ `devops` | 3.6a: triagem dos 5 modelos (estágio 0, um por vez) → finalistas; o tempo por passo e a memória medidos calibram o orçamento da HPO de cada finalista e mostram se o fp16 é estável ∥ storage local do Optuna + repositórios no HF Hub + GGUF base dos 5 modelos para medir a latência no `llama-server` local | `weights/llm/triage/*`, `finetuning/config/hpo_config.yaml` ∥ — |
| **R5** (GPU local — busca) | `ai-specialist` (um candidato por vez na GPU local) | 3.6b: estágio 1 de cada finalista (TPE + Hyperband, estudo próprio) | `weights/llm/hpo/<candidate_id>/*` |
| **R6** (GPU local — confirmação) | `ai-specialist` (idem) | 3.6c: estágio 2 de cada finalista (top-3 + padrão em fidelidade total) e vencedor de cada um pelo score composto | `weights/llm/hpo/<candidate_id>/stage2_comparison.json`, `weights/llm/run_*.json` |
| **R7** (export + registro + docs) | `developer#3` ∥ `ai-specialist` | 3.7 real para cada finalista (merge → GGUF Q4_K_M → upload no bucket e no HF) + 3.9 (registro de todos os candidatos, incluindo a referência Gemini) ∥ 3.8 README + seção E5 com os gráficos da HPO de cada candidato | `weights/llm/registry/*` ∥ `finetuning/README.md`, `docs/fase3/secoes/02-fine-tuning.md` |
| **R8** (Etapa 5 — produção) | `devops` ∥ `tester` | 3.10: imagem `llama-swap` + `llama-server`, configuração gerada a partir do registro, deploy do `healthai-llm` no Cloud Run (free tier) e workflow `deploy-llm.yml` ∥ smoke contra o serviço publicado (ID token, troca entre finalistas, resposta em pt-BR, tempos de carga, troca e resposta, vCPU-s medidos para o orçamento) | `backend/llm_service/*`, `.github/workflows/deploy-llm.yml` ∥ `tests/finetuning/test_llm_service_smoke.py` (marker `integration`) |
| **R9** (Etapa 4) | `reviewer` ∥ `security` ∥ `tester` ∥ `devops` | Revisão ∥ auditoria de acesso ao `healthai-llm` e ao bucket ∥ suíte + smokes no CI ∥ publicação dos adapters (vencedor e padrão de cada candidato) + model cards + conferência do custo no billing | — |

## Código passo a passo
- [ ] **3.1 — `config.py` + YAMLs:** `QLoRAConfig(BaseModel)` com `base_model`, `lora{r, alpha, dropout, target_modules, use_rslora}`, `quantization{load_in_4bit, quant_type="nf4", double_quant, compute_dtype}`, `training{lr, epochs, batch_size, grad_accum, max_seq_length, eval_steps, early_stopping_patience, warmup_ratio, scheduler, weight_decay, neftune_noise_alpha, packing, seed}`, `backend{use_unsloth}`, `paths`. `HPOConfig(BaseModel)` com `search_space`, `warm_start_trials`, `n_trials`, `timeout_hours`, `proxy{train_fraction, max_seq_length, max_steps, eval_steps, eval_subset_size}`, `stage2{top_k, score_weights}`, `storage_url`, `study_name`, `seed`. `load_config(path)` com validação (`r > 0`, `0 ≤ dropout < 1`, pesos somando 1).
- [ ] **3.2 — `data_module.py`:** `load_splits(dir) -> DatasetDict`; `tokenize_with_chat_template(ds, tokenizer, max_len)` (`apply_chat_template`); loss só nas respostas do assistente; `cache_tokenized(ds, path)` (pré-tokenização reutilizada); `make_proxy_split(ds, fraction, seed)` (estratificado por `task_type`); `split_val(ds, eval_subset_size, seed) -> (hpo_eval, selection)`; **template de chat por modelo**: o mesmo template no treino e na inferência (Qwen3 com `enable_thinking=False` nos dois; modelos sem papel `system` no template, como a Gemma, recebem o prompt de sistema mesclado à primeira mensagem do usuário); a triagem confere o template de cada modelo do pool.
- [ ] **3.3 — `train_qlora.py`:** `build_model_and_tokenizer(cfg)` (`BitsAndBytesConfig` ou Unsloth, `prepare_model_for_kbit_training`), `attach_adapter(model, lora_cfg)` / `detach_adapter(model)` (reuso do modelo base entre tentativas), `build_trainer(cfg, model, tok, ds, callbacks)` (`SFTTrainer` com packing + `EarlyStoppingCallback`), `train_once(cfg, ds, callbacks) -> RunResult`, `save_run_artifacts(trainer, cfg)` (adapter em `artifacts/adapters/<run_id>/`; `weights/llm/run_<id>.json` com cfg, sha do dataset, git sha, duração e GPU; `loss_<id>.png`). Flag `--smoke`: `hf-internal-testing/tiny-random-LlamaForCausalLM`, CPU, sem quantização, 2 passos.
- [ ] **3.4 — `finetuning/hpo/`:**
  - `search_space.py`: `suggest_config(trial, base_cfg, space) -> QLoRAConfig` (aplica `alpha = r × ratio` e respeita os fixos); `WARM_START_TRIALS` (padrão `r=16, alpha=32, lr=2e-4, all-linear` + 2 variações conhecidas).
  - `pruning_callback.py`: `OptunaPruningCallback(TrainerCallback)` → em `on_evaluate`, `trial.report(eval_loss, step)` e, se `trial.should_prune()`, levanta `optuna.TrialPruned`.
  - `objective.py`: `build_objective(base_cfg, hpo_cfg, model_cache, proxy_ds) -> Callable[[Trial], float]` (sugere a config → anexa o adapter → treina com o callback → devolve o melhor `eval_loss` → remove o adapter e limpa a memória em `finally`).
  - `selection.py`: `composite_score(run, weights) -> float`, `violates_p040(generations) -> bool`, `pick_winner(stage2_runs) -> RunResult` (desempate pelo menor `r`).
  - `run_hpo.py` (CLI): `python -m finetuning.hpo.run_hpo --stage 1|2 --config …`. O estágio 1 cria ou retoma o estudo (`optuna.create_study(direction="minimize", sampler=TPESampler(multivariate=True, seed), pruner=HyperbandPruner(min_resource=HPO_EVAL_STEPS, max_resource=HPO_MAX_STEPS), storage, load_if_exists=True)`), enfileira o warm start e roda `study.optimize(objective, n_trials, timeout)`. O estágio 2 pega o top-k + o padrão, treina em fidelidade total, gera as respostas de validação e aplica `selection`.
  - `report.py`: exporta `trials.csv`, `best_params.json`, `stage2_comparison.json` e os gráficos (`plot_optimization_history`, `plot_param_importances`, `plot_parallel_coordinate`, `plot_intermediate_values`, versão matplotlib).
- [ ] **3.4a — `finetuning/triage.py`:** `run_triage(pool, cfg) -> TriageResult` (para cada modelo: QLoRA com a config padrão em baixa fidelidade → score composto no `val` de seleção → P-040), `measure_cpu_latency(gguf, threads=4, questions)` (`llama-server` local), `select_finalists(results, max_latency_s=45, tie_margin=2.0, max_finalists=3)` e `export_triage_report()` (`weights/llm/triage/`). A regra e os limites vêm do `hpo_config.yaml` congelado na F0.
- [ ] **3.5 — `finetuning/scripts/` (execução local):** `run_pipeline.sh <candidate_id>` (calibração → `run_hpo --stage 1` → `run_hpo --stage 2` → export), executado no WSL2 dentro de uma sessão `tmux` para sobreviver a desconexões; `huggingface_hub.login` via variável de ambiente; logs em arquivo. Sem lógica nos scripts além da orquestração dos CLIs.
- [ ] **3.6 — Execução na GPU local (por candidato, em sequência):** (a) calibração; (b) estágio 1; (c) estágio 2 e vencedor. Resultados em `weights/llm/hpo/<candidate_id>/` e em `weights/llm/experiments_summary.json` (todos os candidatos, com as horas de GPU gastas).
- [ ] **3.7 — `merge_and_export.py`:** `merge_adapter(base, adapter)`, `convert_to_gguf(merged_dir, quant="Q4_K_M")` (scripts do llama.cpp; o template de chat vai embutido no GGUF, e o system prompt é enviado pela aplicação), `upload_to_gcs(gguf, bucket)`, `push_to_hub(adapter_dir, repo_id)`. Roda para o FT otimizado de cada candidato e também publica o adapter da config padrão (referência para a F10); o merge é feito sobre o modelo base em **fp16** (não sobre o 4-bit), e a conversão usa a **mesma versão do llama.cpp** do servidor; os model cards trazem as licenças e avisos exigidos por cada modelo base (ex.: "Built with Llama" e os termos da Gemma).
- [ ] **3.8 — `finetuning/README.md`:** reprodução ponta a ponta no computador local (WSL2 + GPU NVIDIA com ≥ 6 GB), incluindo como retomar um estudo interrompido e como rodar o `llama-server` local com o GGUF.
- [ ] **3.9 — Registro de modelos:** `app/assistant/llm/registry.py` com `ModelCandidate(BaseModel){candidate_id, display_name, kind: Literal["finetuned", "api", "reference"], base_model, provider: Literal["llama_cpp", "gemini"], serving_ref, selectable, hyperparams, training, artifacts, scorecard: Scorecard | None}` (`serving_ref` = nome do modelo no `llama-swap`, `healthai-med-<candidate_id>`; a URL do serviço vem de `settings.llm_service_url`), `Scorecard{metrics, normalized, group_scores, composite, gates, eligible, evaluated_at, scorecard_config_sha256, test_set_sha256}` e `ModelRegistry(dir)` com `list()`, `get(candidate_id)` e `upsert(candidate)` (escrita atômica e idempotente). `finetuning/register_candidates.py` grava as entradas dos finalistas, dos não finalistas (`kind="reference"`, com o resultado da triagem) e da referência Gemini. A resolução do ativo fica na F7, e a recomendação e ativação na F9 (ver [scorecard de modelos](00-scorecard-modelos.md)).
- [ ] **3.10 — Serviço `healthai-llm` em produção (free tier):** `llm_service/Dockerfile` (`llama-swap` e `llama-server` CPU com versões fixas; usuário não-root; sem pesos na imagem); `llm_service/render_config.py` (gera a configuração do `llama-swap` a partir dos finalistas do registro: um modelo `healthai-med-<candidate_id>` por GGUF em `/models`, `--parallel 1`, `--ctx-size` adequado, **sem `ttl`**: o modelo fica carregado enquanto a instância existir, e a troca descarrega o anterior); `deploy-llm.yml` (build no Artifact Registry e `gcloud run deploy healthai-llm --cpu 4 --memory 4Gi --concurrency 4 --min-instances 0 --max-instances 1 --no-allow-unauthenticated --execution-environment gen2`, com volume do Cloud Storage montado em `/models`, região us-central1). O smoke `tests/finetuning/test_llm_service_smoke.py` chama `/health` e `/v1/chat/completions` com ID token para cada finalista (forçando a troca) e registra tempos de carga, troca e resposta e vCPU-s.

## Critérios de aceite

- Smoke de treino **e** smoke de HPO rodando no CI sem GPU.
- Treinos e HPO feitos no computador pessoal (custo de nuvem zero), com as horas gastas registradas.
- Estudo do Optuna persistido e retomável; `trials.csv` com todas as tentativas (completas e podadas) e os valores intermediários.
- Estágio 2 com top-3 + padrão em fidelidade total e vencedor escolhido pelo score composto no `val` de seleção, nunca no `test`.
- Gráficos da HPO e curvas de loss versionados; adapter vencedor e adapter padrão no HF Hub com model card; GGUF no bucket.
- **Serviço `healthai-llm` publicado no Cloud Run em CPU** com os 2–3 finalistas e só o ativo em memória, sem acesso público, respondendo por ID token, com escala a zero; tempos de carga, troca e resposta e vCPU-s por resposta registrados.
- Triagem dos 5 modelos documentada, com os finalistas escolhidos pela regra pré-registrada.
- Custo do mês da F3 no billing dentro da meta da D14.
- Todos os candidatos (FT otimizado, FT padrão, base e Gemini) registrados em `weights/llm/registry/`, com `scorecard` vazio até a F10.

## Audit

1. `--smoke` gera um adapter carregável com `PeftModel.from_pretrained`.
2. `r=0` → `ValidationError`.
3. `suggest_config` com `FixedTrial` produz `alpha = r × ratio` e mantém os fixos.
4. Callback com pruner que sempre poda → `TrialPruned` na primeira avaliação.
5. Interromper o smoke de HPO e rodar de novo → o estudo continua com o número de tentativas acumulado.
6. Run com uma resposta de prescrição direta → desclassificada pela P-040.
7. Nenhum caminho de código da HPO lê `test.jsonl` (teste que verifica o acesso aos arquivos).
8. `llama-server` local com o GGUF de cada candidato responde "Qual o rastreio para BI-RADS 3?" em pt-BR.
9. Pedido de receita → sugestão com aviso.
10. `ModelRegistry.upsert` duas vezes → mesmo arquivo; entrada inválida → `ValidationError`.
11. Chamada sem token ao `healthai-llm` → 403; com o ID token da service account do backend → resposta do fine-tuned pedido.
12. Depois de ~15 min sem chamadas, o serviço está com 0 instâncias (métrica do Cloud Run).
13. Requisição com o finalista B depois de usar o A → o `llama-swap` descarrega o A, carrega o B e responde; a memória da instância não passa de 4 GiB.
14. Regra da triagem com resultados sintéticos: modelo com latência > 45 s fica fora; 3º a 1,5 ponto do 2º entra; 3º a 3 pontos fica fora.

## Commits

`feat(finetuning): adiciona config validada de treino e hpo` · `feat(finetuning): adiciona data module com proxy e cache de tokenizacao` · `feat(finetuning): adiciona treino qlora com reuso do modelo base e modo smoke` · `feat(finetuning): adiciona busca bayesiana multifidelidade com optuna e poda hyperband` · `feat(finetuning): seleciona config final por score composto com restricao P-040` · `feat(finetuning): exporta gguf para cloud storage e hf hub` · `feat(assistant): adiciona registro de modelos candidatos` · `feat(finetuning): adiciona triagem dos modelos base com regra pre-registrada` · `feat(llm-service): serve finalistas em cpu no cloud run com troca sob demanda via llama-swap` · `ci: adiciona deploy do servico healthai-llm`

## Entrega para as próximas fases

O resultado da triagem dos 5 modelos; um fine-tuned otimizado **por finalista**, servido em produção pelo `healthai-llm` (CPU, free tier, privado, só o ativo em memória); os adapters vencedor e padrão de cada finalista no HF; os GGUF dos finalistas no bucket; e o **registro de modelos** com todos (sem scorecard). O provider e o aquecimento da F7 usam o registro, a F9 exibe os finalistas no painel e a F10 calcula os scorecards. Na F11: `weights/llm/triage/*` e `weights/llm/hpo/*` para a seção E5.