# Roadmap do Projeto 🗺️

> **Localização Mandatória:** `.agents/docs/ROADMAP.md`  
> **Responsável:** Product Owner (`product_owner.md`) / `agile-coach`

---

## 1. Visão do Produto
A plataforma **HealthAI** é um ecossistema inteligente de apoio à decisão clínica e logística hospitalar, composto por triagem médica preditiva multimodal (Câncer de Mama e Síndrome dos Ovários Policísticos), explicabilidade diagnóstica via Inteligência Artificial Generativa (LLMs) e roteamento de veículos hospitalares para distribuição de medicamentos e insumos médicos (VRP).

---

## 2. Épicos e User Stories (Backlog)

### [CONCLUÍDO] Fase 1: Triagem Diagnóstica Multimodal Serverless
- [x] **US-01:** Anamnese de saúde feminina com formulários dinâmicos de triagem clínica.
- [x] **US-02:** Treinamento de modelos tabulares clássicos (Random Forest, SVM, KNN, Regressão Logística, MLP, Gradient Boosting).
- [x] **US-03:** Classificação de imagens de mamografia utilizando Redes Convolucionais PyTorch (ResNet50).
- [x] **US-04:** Painel Administrativo com seleção de modelos ativos em tempo real.
- [x] **US-05:** Deploy serverless em Google Cloud Run e Firebase Hosting.

---

### [EM ANDAMENTO] Fase 2: Otimização de Modelos & Roteamento Logístico Inteligente
- [ ] **US-06 (Projeto 1 - AG Hiperparâmetros):** Otimização de hiperparâmetros dos modelos de diagnóstico clínico via Algoritmos Genéticos, com codificação cromossômica mista, operadores de mutação/crossover e função fitness focada em Recall/Sensibilidade ($F_2$-Score).
- [ ] **US-07 (Projeto 1 - Experimentos & Benchmarks):** Execução de 3 experimentos sistemáticos com o AG para Câncer e PCOS, gerando tabela comparativa com baseline da Fase 1 e persistência dos pesos otimizados.
- [ ] **US-08 (Projeto 1 - Explicabilidade LLM):** Integração com LLM (Gemini/OpenAI) para transformar dados laboratoriais e predições em laudos médicos estruturados em linguagem natural com insights acionáveis.
- [ ] **US-09 (Projeto 2 - Matriz de Tempos OSRM):** Camada de mapas com OSRM/OpenStreetMap em 1 única requisição batch com cache local persistente em SQLite para cálculo de grafos viários reais sem custos de API.
- [ ] **US-10 (Projeto 2 - Roteamento VRP com AG):** Algoritmo Genético para o Caixeiro Viajante e Roteamento de Veículos (VRP) com restrições de prioridade de medicamentos críticos, volume/peso refrigerado, autonomia e múltiplos veículos.
- [ ] **US-11 (Projeto 2 - Nova Rota & Mapa Interativo):** Nova rota no backend FastAPI (`/api/v1/routes`) e tela SPA Angular (`/routes`) com mapa Leaflet, marcadores temáticos, polilinhas por veículo e telemetria de convergência.
- [ ] **US-12 (Projeto 2 - LLM Logística):** Geração de itinerários passo a passo para motoristas, relatórios executivos de eficiência e assistente Q&A em linguagem natural sobre as rotas.

---

### [PLANEJADO] Fase 3: Assistente Médico Personalizado (Fine-tuning + LangChain + LangGraph)
> Plano detalhado (índice + um arquivo por fase F0–F11, matriz de rastreabilidade com o PDF, agentes, rodadas, critérios e testes): `.agents/docs/plans/INDEX.md`

- [ ] **US-13 (F0 - Fundação):** ADRs, regras P-040 a P-052, RIPD, dependências e esqueleto modular do assistente.
- [ ] **US-14 (F1 - Corpus):** Coleta de PubMedQA/MedQuAD e geração do corpus interno sintético (protocolos, FAQ de médicos, laudos, receitas e procedimentos).
- [ ] **US-15 (F2 - Dados):** Preprocessing, anonimização pt-BR com gate de PII e curadoria do dataset de instruções.
- [ ] **US-16 (F3 - Fine-tuning):** Triagem de 5 modelos base, QLoRA (TRL + PEFT) com HPO no Optuna, export GGUF e publicação no serviço `healthai-llm` (Cloud Run, CPU).
- [ ] **US-17 (F4 - Prontuários):** Base estruturada sintética (pacientes, exames, condutas, alertas, auditoria) com repositórios, no Postgres do Supabase.
- [ ] **US-18 (F5 - Segurança):** Guardrails de escopo e de prescrição, auditoria estruturada com `trace_id` e contrato de resposta explicável.
- [ ] **US-19 (F6 + F7 - Assistente LangChain):** RAG com pgvector, busca híbrida e metadados de fonte + pipeline LangChain com a LLM customizada, tools de prontuário e citações.
- [ ] **US-20 (F8 - LangGraph):** Fluxo automatizado paciente → exames pendentes → alertas → sugestão → aprovação humana.
- [ ] **US-21 (F9 - API e UI):** Endpoints do assistente, perfil médico com JWT em cookie HttpOnly e tela de chat com fontes e aprovação.
- [ ] **US-22 (F10 + F11 - Avaliação e Entrega):** Avaliação base vs fine-tuned, relatório técnico, README, CI e vídeo de até 15 min.

---

## 3. Histórico de Entregas
- **2026-09 - Fase 1 Concluída:** Anamnese preditiva multimodal, modelos tabulares, CNN ResNet50 e painel administrativo em produção no Cloud Run e Firebase Hosting.
