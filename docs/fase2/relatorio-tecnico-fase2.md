# Relatório Técnico Consolidado - Tech Challenge: Fase 2 🏥🚀

> **Pós-Graduação em Inteligência Artificial para a Saúde**  
> **Instituição:** FIAP  
> **Status:** Entrega Completa de Ambos os Projetos (Projeto 1: Modelos + LLM & Projeto 2: Rotas VRP + Mapas + LLM)  
> **Repositório do Projeto:** [Github: Health AI](https://github.com/D4NL18/tech-challenge-health-ai)

---

## 1. Introdução e Contextualização do Desafio

Após o sucesso inicial no desenvolvimento de modelos de *Machine Learning* para diagnóstico médico preditivo na Fase 1 (triagem de Câncer de Mama e Síndrome dos Ovários Policísticos - SOP), a plataforma hospitalar **HealthAI** avançou para a **Fase 2** com o objetivo de solucionar dois desafios centrais da medicina moderna através de **Algoritmos Genéticos (AG)** e **Processamento de Linguagem Natural com Modelos de Linguagem de Grande Escala (LLMs)**:

1. **Projeto 1 (Otimização de Modelos de Diagnóstico):** Superar as limitações da busca estática por hiperparâmetros (GridSearch), utilizando um algoritmo genético que otimiza classificadores clínicos com base na sensibilidade diagnóstica ($F_2$-Score / Recall), aliado à geração de laudos médicos explicativos em linguagem natural via LLMs para transformar probabilidades frias em decisões terapêuticas interpretáveis.
2. **Projeto 2 (Otimização de Rotas para Medicamentos e Insumos):** Desenvolver um sistema de roteamento logístico para frotas hospitalares resolvendo o problema do Caixeiro Viajante com Múltiplos Veículos e Capacidade (CVRP/VRPTW), incorporando restrições do mundo real (medicamentos de urgência crítica, cadeia de frio 2°C a 8°C, capacidade volumétrica e autonomia de combustível), operando sobre grafos viários reais ponderados por tempo via **OSRM / OpenStreetMap (Custo Zero de API)** e gerando itinerários operacionais e relatórios executivos via LLMs.

Em vez de optar por apenas um dos caminhos, este trabalho implementou e integrou **ambos os projetos** em uma arquitetura de microsserviços modular, escalável e de baixíssimo custo.

---

## 2. PROJETO 1: Otimização de Modelos de Diagnóstico

### 2.1. Implementação do Algoritmo Genético de Hiperparâmetros

#### A. Representação Genética (Codificação Cromossômica)
O espaço de busca tradicional por grade discreta (*GridSearchCV*) foi substituído por uma **codificação cromossômica híbrida** capaz de transitar fluidamente entre genes inteiros, reais (escalas lineares e logarítmicas) e categóricos:
- **`n_estimators` (Gene Inteiro):** Intervalo contínuo $[20, 250]$, permitindo ao algoritmo encontrar números intermediários ideais de árvores sem saltos arbitrários.
- **`max_depth` (Gene Inteiro ou None):** Intervalo $[3, 25]$ ou ausência de restrição de profundidade, controlando *overfitting* de forma estocástica.
- **`min_samples_split` e `min_samples_leaf` (Genes Inteiros):** Intervalos $[2, 15]$ e $[1, 8]$, regrando a pureza dos nós folha.
- **`criterion` (Gene Categórico):** Escolha dinâmica entre Gini, Entropia e Log-Loss.

#### B. Operadores Genéticos Especializados
1. **Seleção por Torneio ($k=3$):** Sorteia três indivíduos da população e elege o de maior aptidão clínica. Esse operador mantém uma pressão seletiva balanceada, evitando convergência prematura para mínimos locais.
2. **Elitismo Estrito ($E=2$):** Preserva intactos os dois indivíduos mais aptos de cada geração para a seguinte, garantindo monotonicidade não-decrescente da melhor aptidão encontrada.
3. **Cruzamento (Crossover) Misto:** Recombinação uniforme para genes discretos e categóricos, combinada com *Crossover Aritmético* para hiperparâmetros contínuos com fator $\alpha \sim U(0, 1)$.
4. **Mutação Gaussiana com Limites Rígidos (*Bounds*):** Aplica perturbação normal $\mathcal{N}(0, \sigma^2)$ re-clipada aos limites permitidos de cada hiperparâmetro, impedindo a geração de configurações inválidas perante o Scikit-Learn.

#### C. Função Fitness Clínica ($F_2$-Score Ponderado)
Em triagem oncológica e ginecológica, a métrica de Acurácia global é insuficiente e perigosa: um **Falso Negativo** (não diagnosticar uma paciente com câncer) tem consequências clínicas irreversíveis, enquanto um Falso Positivo acarreta apenas exames complementares confirmatórios.

Por esse motivo, formulamos a função fitness utilizando o **$F_2$-Score com Validação Cruzada Estratificada em 5 Dobras ($5$-Fold Stratified CV)**:
$$\text{Fitness} = F_2 = 5 \cdot \frac{\text{Precision} \cdot \text{Recall}}{4 \cdot \text{Precision} + \text{Recall}}$$
Ao quadruplicar o peso relativo do Recall (Sensibilidade), o Algoritmo Genético é impelido a penalizar severamente qualquer cromossomo que deixe casos positivos escaparem, mesmo que isso represente ligeira redução na precisão nominal.

---

### 2.2. Resultados dos 3 Experimentos Sistemáticos

Foram executados três experimentos controlados com progressão de complexidade sobre o dataset de Câncer de Mama:

| Métrica / Experimento | Baseline Fase 1 (GridSearch) | Exp 1: Convergência Rápida (Pop 20 / Gen 10) | Exp 2: Exploração Balanceada (Pop 40 / Gen 20) | Exp 3: Otimização Robusta (Pop 80 / Gen 30) |
| :--- | :---: | :---: | :---: | :---: |
| **Tempo de Execução** | ~15 s | 188.54 s | 669.67 s | 1712.04 s |
| **Recall (Sensibilidade)** | 0.9048 | **0.9528 (+5.3%)** | **0.9576 (+5.8%)** | **0.9576 (+5.8%)** |
| **F2-Score Clínico** | 0.9135 | **0.9527 (+4.3%)** | **0.9566 (+4.7%)** | **0.9566 (+4.7%)** |
| **Acurácia Global (5 Folds)**| 0.9474 | **0.9649 (+1.8%)** | **0.9666 (+2.0%)** | **0.9666 (+2.0%)** |
| **F1-Score** | 0.9268 | **0.9530 (+2.8%)** | **0.9554 (+3.1%)** | **0.9554 (+3.1%)** |
| **ROC-AUC Médio** | 0.9780 | **0.9916** | **0.9916** | **0.9916** |

**Conclusão Empírica:** O **Experimento 2** atingiu o ápice de sensibilidade diagnóstica (Recall de 95.76% e F2 de 95.66%) com tempo de treino três vezes menor do que o Experimento 3, consolidando-se como o modelo ótimo implementado e salvo no arquivo `weights/modelo_random_forest_cancer_genetic.pkl`.

---

### 2.3. Integração com LLMs: Explicabilidade e Laudos Clínicos

Para transpor a barreira de "caixa-preta" dos algoritmos e capacitar o profissional de saúde a tomar decisões ágeis, foi implementado o serviço `ClinicalLLMService` em `backend/app/services/clinical_llm.py`:
- **Abordagem de Prompt Engineering:** Injeção de Persona Médica Especialista em conjunto com raciocínio clínico passo a passo (*Chain-of-Thought*). A LLM é instruída a correlacionar os percentis laboratoriais anormais (ex: concavidade celular $> 0.28$, raio nuclear expandido) com a probabilidade final inferida.
- **Saída Estruturada (Pydantic Schema):** O modelo devolve obrigatoriamente um JSON parseável composto por:
  1. *Resumo do Caso:* Síntese em linguagem natural da condição da paciente.
  2. *Top 3 Fatores de Risco:* Identificação das anomalias citológicas mais determinantes.
  3. *Raciocínio Clínico:* Justificativa do índice probabilístico gerado.
  4. *Recomendações Médicas:* Sugestões de condutas, biópsias (ex: Core Biopsy guiada por USG) e encaminhamentos em prazos clínicos seguros.
  5. *Aviso Ético e Legal:* Disclaimer explícito delimitando o caráter complementar e de suporte à decisão clínica.
- **Resiliência e Fallback Heurístico:** Se as chaves de API externas (Gemini/OpenAI) estiverem sem cota ou indisponíveis, um motor heurístico com protocolos clínicos pré-estabelecidos gera o laudo instantaneamente, assegurando 100% de disponibilidade.

---

## 3. PROJETO 2: Otimização de Rotas para Medicamentos e Insumos

### 3.1. Arquitetura de Mapas com OSRM / OpenStreetMap (Custo Zero e Grafo Real)

> [!IMPORTANT]
> **Estratégia Anti-Esgotamento de Cotas:**
> A avaliação da função fitness de um Algoritmo Genético realiza milhares de cálculos (ex: 50 indivíduos $\times$ 30 gerações = 1.500 avaliações). Bater em APIs pagas de mapas (como Google Maps Distance Matrix) durante o loop geraria custos imprevisíveis e esgotamento de cotas.

Nossa arquitetura resolveu essa equação através do padrão de **Duas Camadas com Cache Persistente**:
1. **Camada 1 (Matriz de Adjacência em Batch Único):** Antes de iniciar a evolução, o sistema envia todos os $N$ nós para o endpoint `/table/v1/driving/` do **OSRM (Open Source Routing Machine)**. Em **1 única chamada HTTP gratuita**, obtém-se a matriz completa $N \times N$ de tempos (segundos) e distâncias (metros), ponderadas por regras de trânsito reais do OpenStreetMap (velocidades máximas das vias, sentidos únicos e manobras permitidas).
2. **Camada de Cache Local (SQLite):** Os tempos e distâncias são persistidos em `backend/data/geo_cache.db`. Consultas repetidas aos mesmos hospitais consomem **zero requisições de rede**.
3. **Camada 2 (Execução do AG em RAM):** As milhares de iterações genéticas acontecem 100% em memória RAM em microssegundos ($O(1)$ sobre arrays bidimensionais).
4. **Resolução de Polilinha:** Apenas a rota campeã é submetida ao endpoint OSRM `/route/` em 1 chamada para obter o traçado exato das ruas (GeoJSON) para projeção no mapa interativo **Leaflet.js** no Angular.

---

### 3.2. Modelagem do Algoritmo Genético de Roteamento (VRP)

- **Cromossomo de Permutação:** Vetor contendo a sequência ordenada das paradas $[d_1, d_2, \dots, d_M]$ e algoritmo de particionamento dinâmico entre $K$ veículos da frota.
- **Operador Order Crossover (OX):** Preserva blocos de rotas viáveis e preenche os demais nós na ordem do segundo progenitor, eliminando 100% dos riscos de nós duplicados ou omitidos.
- **Mutação por Inversão 2-opt e Swap:** O operador 2-opt desfaz cruzamentos ineficientes de vias ("laços"), que é o padrão ouro na literatura de otimização de rotas.
- **Função Fitness Multiobjetivo com Restrições Médicas:**
  $$\text{Fitness} = \text{TempoTotalViagem(min)} + \lambda_1 \cdot \text{AtrasoCrítico} + \lambda_2 \cdot \text{SobrecargaBaú} + \lambda_3 \cdot \text{ExcessoAutonomia}$$
  - **Medicamentos Críticos (Prioridade Máxima):** Medicamentos biológicos, vacinas e bolsas de sangue refrigeradas sofrem penalidade cumulativa por tempo de espera caso não sejam posicionadas nas primeiras paradas do itinerário.
  - **Capacidade do Veículo:** Penalidade proporcional a cada kg que exceder o limite do compartimento refrigerado.
  - **Autonomia da Frota:** Penalidade caso a quilometragem total ultrapasse a autonomia estipulada para a jornada.

---

### 3.3. Integração com LLMs: Roteiros Operacionais e Assistente Logístico

O serviço `LogisticsLLMService` em `backend/app/services/logistics_llm.py` foi integrado para:
1. **Roteiro do Motorista:** Geração de ordens de serviço humanizadas com alertas destacados sobre manutenção térmica (2°C a 8°C), conferência de lacres e exigência de carimbos farmacêuticos.
2. **Relatório Executivo de Eficiência:** Relatório executivo consolidando economia estimada de tempo (~28% a menos de exposição de insumos em trânsito), redução de quilometragem percorrida (~32%) e redução de emissões de CO2.
3. **Chatbot Logístico Interativo:** Canal de perguntas e respostas em linguagem natural, permitindo aos gestores consultar quais veículos transportam cargas críticas e os tempos previstos de chegada.

---

## 4. Frontend Angular e Nova Rota de Mapas (`/routes`)

No Frontend, foi desenvolvida a nova rota SPA `/routes` ([`MedicalRoutesComponent`](file:///c:/Users/PC/Documents/GitHub/tech-challenge-health-ai/frontend/src/app/pages/medical-routes/medical-routes.component.ts)), contendo:
- **Mapa Interativo (Leaflet.js + OpenStreetMap):** Renderização de mapa com marcadores customizados (Hub Hospitalar vermelho, Entregas Urgentes laranjas e Insumos regulares azuis) e traçado das polilinhas coloridas por veículo.
- **Cenário de Teste em São Paulo:** Botão de carregamento instantâneo de 10 nós reais (Hospital das Clínicas da FMUSP, Santa Casa de São Paulo, UBS Bela Vista, UBS Santa Cecília, Hospital São Paulo/UNIFESP, etc.).
- **Painel de Parâmetros e Telemetria:** Sliders para calibrar tamanho da frota, capacidade de carga, população e gerações do AG, acompanhado por cards de métricas de tempo e distância.
- **Abas Operacionais:** Alternância intuitiva entre Itinerário, Roteiro do Motorista (LLM), Relatório de Eficiência (LLM) e Chatbot com IA.

---

## 5. Qualidade de Software, Testes e Conformidade com a LGPD

- **Testes Automatizados:** Suíte completa com `pytest` (11 testes automatizados) validando:
  - Codificação cromossômica e podagem de limites de hiperparâmetros.
  - Operadores de mutação e crossover OX livres de duplicidade.
  - Penalizações da função fitness para medicamentos críticos e sobrecarga.
  - Persistência e integridade do cache SQLite de mapas.
  - Endpoints REST da FastAPI (`/api/v1/routes/optimize`, `/instructions`, `/report`, `/explain-diagnosis`).
- **Privacidade e LGPD (Lei 13.709/2018):**
  - Aplicação estrita do princípio da **Minimização de Dados**: a arquitetura opera em modo *Stateless* para o diagnóstico (dados clínicos não são mantidos em banco persistente de pacientes).
  - Enquadramento legal para tratamento de dados sensíveis de saúde sob a base da **Tutela da Saúde** (Art. 11, II, 'f' da LGPD).
  - Logs da aplicação sanitizados contra vazamento de informações de identificação pessoal (PII).

---

## 6. Conclusão

A entrega da **Fase 2 do Tech Challenge** superou os requisitos propostos ao entregar **ambos os projetos integrados de ponta a ponta**. O projeto demonstrou como a Inteligência Artificial pode atuar de forma pragmática na saúde pública e privada: elevando a precisão diagnóstica através de Algoritmos Genéticos que priorizam vidas (Recall), conferindo transparência ética com laudos explicativos via LLM e resolvendo a complexa malha logística hospitalar de distribuição de medicamentos em grafos de mapas reais sem nenhum custo de infraestrutura de API.
