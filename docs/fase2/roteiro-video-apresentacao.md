# Roteiro Oficial de Vídeo de Apresentação — Tech Challenge Fase 2 (FIAP 7IADT)

> **Duração Estimada:** 12 a 15 minutos (Limite máximo FIAP: 15 minutos)
> **Escopo:** Demonstração integrada do **Projeto 1** (Otimização Evolucionária de Hiperparâmetros de Modelos de Diagnóstico com AG + Interpretabilidade Clínica com LLM) e do **Projeto 2** (Otimização de Rotas Médicas Hospitalares TSP/VRP com AG sobre Malha Viária Real OSRM + Inteligência Logística com LLM), alinhado integralmente ao [Relatório Técnico da Fase 2](file:///c:/GitHub/tech-challenge-health-ai/docs/fase2/relatorio-tecnico-fase2.md).

---

## Checklist de Preparação Antes de Gravar

1. **Subir o Backend FastAPI** (Terminal 1 na pasta `backend/`):
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```
2. **Subir o Frontend Angular 19** (Terminal 2 na pasta `frontend/`):
   ```bash
   npm start
   ```
3. **Deixar abertos no navegador (`http://localhost:4200`)**:
   - Aba 1: `/admin` (Painel de Governança MLOps e Evolução Genética de Hiperparâmetros)
   - Aba 2: `/dashboard` (Triagem e Explicação Clínica via Gemini LLM)
   - Aba 3: `/routes` (Otimizador de Rotas Médicas e Distribuição de Insumos VRP + Leaflet.js + LLM)
   - Aba 4: `http://localhost:8000/docs` (Swagger UI da API unificada v2.0.0)
4. **Deixar o VS Code aberto** com os arquivos-chave em abas:
   - [relatorio-tecnico-fase2.md](file:///c:/GitHub/tech-challenge-health-ai/docs/fase2/relatorio-tecnico-fase2.md)
   - Projeto 1: [chromosome.py](file:///c:/GitHub/tech-challenge-health-ai/backend/app/genetic/hyperopt/chromosome.py), [operators.py](file:///c:/GitHub/tech-challenge-health-ai/backend/app/genetic/hyperopt/operators.py), [fitness.py](file:///c:/GitHub/tech-challenge-health-ai/backend/app/genetic/hyperopt/fitness.py), [optimizer.py](file:///c:/GitHub/tech-challenge-health-ai/backend/app/genetic/hyperopt/optimizer.py) e [clinical_llm.py](file:///c:/GitHub/tech-challenge-health-ai/backend/app/services/clinical_llm.py)
   - Projeto 2: [osrm_provider.py](file:///c:/GitHub/tech-challenge-health-ai/backend/app/services/geo/osrm_provider.py), [vrp_chromosome.py](file:///c:/GitHub/tech-challenge-health-ai/backend/app/genetic/routing/vrp_chromosome.py), [routing_operators.py](file:///c:/GitHub/tech-challenge-health-ai/backend/app/genetic/routing/routing_operators.py), [routing_fitness.py](file:///c:/GitHub/tech-challenge-health-ai/backend/app/genetic/routing/routing_fitness.py), [vrp_solver.py](file:///c:/GitHub/tech-challenge-health-ai/backend/app/genetic/routing/vrp_solver.py) e [logistics_llm.py](file:///c:/GitHub/tech-challenge-health-ai/backend/app/services/logistics_llm.py)

---

## Bloco 1: Abertura e Arquitetura Unificada da Fase 2 (00:00 – 01:30)

**Tela:** Mostrar o [Relatório Técnico da Fase 2](file:///c:/GitHub/tech-challenge-health-ai/docs/fase2/relatorio-tecnico-fase2.md) aberto no VS Code ou navegador e o Swagger UI (`http://localhost:8000/docs`).

**Roteiro de Fala:**
> "Olá! Neste vídeo vamos apresentar a entrega completa da Fase 2 do Tech Challenge de Inteligência Artificial para Devs na área de Saúde.
>
> Nesta fase, nós evoluímos a plataforma construída na Fase 1 implementando integralmente **ambos os projetos propostos** no desafio:
> 1. No **Projeto 1**, substituímos os hiperparâmetros fixos da Fase 1 por um motor completo de **Algoritmos Genéticos (`app/genetic/hyperopt/`)** que evolui populações de cromossomos híbridos para otimizar o **$F_2$-Score** (que atribui peso 4 vezes maior ao Recall clínico em relação à Precisão), acoplado ao **Google Gemini (`gemini-2.5-flash`)** para transformar as probabilidades matemáticas e importâncias de variáveis em relatórios médicos explicáveis.
> 2. No **Projeto 2**, construímos um sistema de **Otimização Logística Hospitalar TSP/VRP (`app/genetic/routing/`)** sobre a malha viária real do OpenStreetMap via OSRM com cache persistente em SQLite, resolvendo o roteamento de frotas com restrições de capacidade, autonomia, janelas de prioridade clínica em 3 níveis e integração com LLMs para gerar ordens de serviço de motoristas, relatórios executivos de emissões de $\text{CO}_2$ e assistente conversacional."

---

## Bloco 2: Projeto 1 — Código e Lógica do Algoritmo Genético de Hiperparâmetros (01:30 – 04:30)

**Tela:** Alternar no VS Code entre [chromosome.py](file:///c:/GitHub/tech-challenge-health-ai/backend/app/genetic/hyperopt/chromosome.py), [operators.py](file:///c:/GitHub/tech-challenge-health-ai/backend/app/genetic/hyperopt/operators.py), [fitness.py](file:///c:/GitHub/tech-challenge-health-ai/backend/app/genetic/hyperopt/fitness.py) e [optimizer.py](file:///c:/GitHub/tech-challenge-health-ai/backend/app/genetic/hyperopt/optimizer.py).

**Roteiro de Fala:**
> "Vamos começar pelo código do **Projeto 1**, localizado em `backend/app/genetic/hyperopt/`.
>
> 1. **Representação Genética (`chromosome.py`):**
>    Na classe `HyperparameterGeneSpace`, mapeamos o espaço de busca de 6 famílias de algoritmos (`random_forest`, `svm`, `gradient_boosting`, `mlp`, `knn` e `logistic_regression`) com codificação híbrida: genes inteiros (`int`), inteiros anuláveis (`int_or_none` para `max_depth`), reais contínuos (`float`), reais em escala logarítmica base 10 (`float_log` para `C`, `gamma` e `learning_rate`, garantindo amostragem uniforme entre $10^{-4}$ e $10^{2}$) e categóricos (`cat`). O método `to_sklearn_estimator()` decodifica o genótipo diretamente em um estimador válido do Scikit-Learn, aplicando correção de compatibilidade de solvers e tuplas de camadas ocultas na MLP.
>
> 2. **Operadores Genéticos (`operators.py`):**
>    Na classe `GeneticOperators`, implementamos duas modalidades de seleção: **Seleção por Torneio ($k=3$)** e **Seleção por Roleta** proporcional ao fitness. No método `crossover()`, aplicamos um cruzamento híbrido: genes numéricos sofrem **Crossover Aritmético Ponderado** ($\alpha \cdot g_1 + (1-\alpha) \cdot g_2$), enquanto genes categóricos ou anuláveis sofrem **Crossover Uniforme**. Já no método `mutate()`, aplicamos perturbação Gaussiana proporcional à amplitude do domínio — e diretamente no expoente $\log_{10}$ para genes `float_log` — com reflexão/truncamento estrito nos limites `[low, high]`.
>
> 3. **Função de Fitness Clínica (`fitness.py`):**
>    Na classe `ClinicalFitnessEvaluator`, cada cromossomo é avaliado com Validação Cruzada Estratificada de 5 Folds (`StratifiedKFold`). Para evitar qualquer *Data Leakage*, instanciamos um `Pipeline` que ajusta o `StandardScaler` exclusivamente dentro dos folds de treino. Como em triagem oncológica um Falso Negativo é muito mais crítico que um Falso Positivo, nossa função objetivo maximiza o **$F_2$-Score** ($\beta = 2$), que dá peso 4 vezes maior à Sensibilidade (Recall).
>
> 4. **Loop Evolutivo e Visualização (`optimizer.py` e `visualizer.py`):**
>    A classe `GeneticHyperparameterOptimizer` gerencia a evolução geração a geração com **Elitismo configurável ($E=2$)**, preservando intactos os 2 melhores indivíduos, monitora o `diversity_ratio` da população e suporta plotagem em tempo real (`--live-plot`) via `matplotlib.pyplot.ion()`."

---

## Bloco 3: Projeto 1 — Experimentos, Benchmarks (Fase 1 vs Fase 2) e Demo com LLM (04:30 – 07:30)

**Tela:**
1. Mostrar no terminal ou no [Relatório Técnico da Fase 2](file:///c:/GitHub/tech-challenge-health-ai/docs/fase2/relatorio-tecnico-fase2.md) as tabelas dos 3 Experimentos de AG e do Benchmark Multimodelo.
2. No navegador, abrir `/admin` e `/dashboard`.

**Roteiro de Fala:**
> "Executamos a bateria sistemática de experimentos através do script `train_genetic_hyperopt.py`:
> - Testamos **3 configurações evolutivas** no Random Forest para Câncer de Mama:
>   - **Experimento 1 (Rápido):** População 20, 10 gerações, mutação 10%.
>   - **Experimento 2 (Balanceado):** População 40, 20 gerações, mutação 15%.
>   - **Experimento 3 (Robusto):** População 80, 30 gerações, mutação 20%.
> - Comparando com o **Baseline da Fase 1** (hiperparâmetros manuais), o Recall no conjunto de teste saltou de **90,48% na Fase 1 para 95,76% na Fase 2 (+5,28 pontos percentuais)**, o $F_2$-Score evoluiu de **0,9135 para 0,9566 (+4,31%)** e no Experimento 3 a Acurácia atingiu **96,84%** com ROC-AUC de **0,9916**, reduzindo drasticamente os Falsos Negativos.
> - Além disso, na busca multimodelo entre os 6 classificadores, a rede neural **MLP otimizada por AG** atingiu **$F_2$-Score de 0,9717 e Recall de 97,18%** em Câncer de Mama, enquanto em **SOP (PCOS)** o **SVM otimizado por AG** alcançou **$F_2$-Score de 0,8633**.
>
> *(Mostrar a aba `/admin` no navegador)*
> Aqui na tela de Governança MLOps (`/admin`), podemos inspecionar os parâmetros campeões descobertos pelo AG, comparar as métricas com o baseline e disparar um novo ciclo evolutivo ao vivo clicando em **Otimizar Hiperparâmetros (AG)**, acompanhando a curva de evolução do Fitness (Melhor vs. Média da População) geração a geração.
>
> *(Mudar para a aba `/dashboard` e executar uma predição clínica seguida de clique em 'Gerar Explicação Clínica com IA')*
> E para fechar o Projeto 1 com IA Generativa, no serviço `clinical_llm.py` (`POST /api/v1/anamnesis/explain-diagnosis`), integramos o **Google Gemini (`gemini-2.5-flash`)** usando *Role Prompting*, *Chain-of-Thought* e saída estruturada validada pelo schema Pydantic `ClinicalReportSchema`. Como vemos na tela, o modelo traduz a probabilidade matemática e as features de maior peso em um parecer estruturado em linguagem natural com resumo executivo, fatores de risco correlacionados, condutas sugeridas e aviso ético obrigatório — contando ainda com fallback determinístico caso a chave de API não esteja configurada."

---

## Bloco 4: Projeto 2 — Código e Lógica do Otimizador de Rotas Médicas VRP + OSRM (07:30 – 11:00)

**Tela:** Alternar no VS Code entre [osrm_provider.py](file:///c:/GitHub/tech-challenge-health-ai/backend/app/services/geo/osrm_provider.py), [vrp_chromosome.py](file:///c:/GitHub/tech-challenge-health-ai/backend/app/genetic/routing/vrp_chromosome.py), [routing_operators.py](file:///c:/GitHub/tech-challenge-health-ai/backend/app/genetic/routing/routing_operators.py), [routing_fitness.py](file:///c:/GitHub/tech-challenge-health-ai/backend/app/genetic/routing/routing_fitness.py) e [vrp_solver.py](file:///c:/GitHub/tech-challenge-health-ai/backend/app/genetic/routing/vrp_solver.py).

**Roteiro de Fala:**
> "Agora vamos ao **Projeto 2: Otimização de Rotas Médicas e Distribuição de Insumos (TSP/VRP)**.
>
> 1. **Grafo Viário Real em 2 Camadas (`osrm_provider.py` e `geo_cache.py`):**
>    Um erro comum em algoritmos genéticos de rotas é consultar APIs de mapas dentro do loop de fitness, o que causaria milhares de chamadas HTTP. Nós resolvemos isso com uma arquitetura em duas camadas:
>    - **Camada 1 (Pré-Otimização):** Fazemos uma única requisição em lote à Table API do OSRM (`/table/v1/driving/`), obtendo a matriz real $N \times N$ de tempos de condução e distâncias nas vias do OpenStreetMap. Essa matriz é salva em cache local SQLite (`geo_cache.db`) indexada por hash MD5 das coordenadas. Se o servidor OSRM estiver inacessível, o sistema aciona automaticamente um fallback Haversine corrigido por fator de sinuosidade urbana de $1,35\times$ a $35\text{ km/h}$.
>    - **Camada 2 (Pós-Otimização):** Apenas para as rotas vencedoras da última geração, consultamos a Route API (`/route/v1/driving/?overview=full&geometries=geojson`) para desenhar as polilinhas exatas das ruas e avenidas no mapa.
>
> 2. **Codificação e Operadores Especializados (`vrp_chromosome.py` e `routing_operators.py`):**
>    Cada cromossomo (`VRPChromosome`) é uma permutação de inteiros $[1, \dots, N]$ sem repetição de paradas. Para preservar a validade da permutação durante a evolução:
>    - Na inicialização, combinamos indivíduos aleatórios com **Hotstart Heurístico Guloso (Nearest-Neighbor)** estratificado por prioridade (`CRITICAL` $\to$ `HIGH` $\to$ `REGULAR`).
>    - No cruzamento (`order_crossover_ox`), implementamos o **Order Crossover (OX)**, que copia uma subsequência contínua do Pai 1 e preenche o restante na ordem relativa do Pai 2 sem gerar duplicatas.
>    - Na mutação (`mutate_route`), combinamos **Mutação por Inversão 2-Opt (70% de chance)** — que inverte um trecho da rota para desfazer cruzamentos geométricos de vias em 'X' — com **Swap Mutation (30% de chance)**.
>
> 3. **Particionamento Multi-Veículo em 3 Níveis Clínicos e Fitness (`vrp_solver.py` e `routing_fitness.py`):**
>    No método `split_chromosome_into_routes`, implementamos uma lógica hospitalar realista em 3 estágios:
>    - **Fase 1 (`CRITICAL` — Cadeia de Frio/Emergências):** O método `_distribute_critical_balanced` aloca paradas críticas sempre no **1º trecho saindo direto do Hub Hospitalar**, distribuindo-as entre as ambulâncias disponíveis para minimizar o tempo máximo de chegada (*urgency makespan*).
>    - **Fase 2 (`HIGH` — Urgência Regional):** As paradas de alta prioridade são agrupadas geograficamente via semeadura angular + *Cheapest Insertion*, criando setores contíguos para cada veículo sem sobreposição de territórios.
>    - **Fase 3 (`REGULAR` — Corredor de Passagem / On-the-Way Insertion):** Se uma entrega regular estiver exatamente no caminho de uma entrega `HIGH` (desvio marginal $\le 4\text{ min}$ ou $\le 25\%$ do trecho), o veículo já aproveita a viagem para entregá-la na passagem; caso contrário, ela fica no final do turno.
>    Tudo isso é avaliado pela função de Fitness em `RouteFitnessEvaluator`, que soma o tempo real de condução OSRM com penalidades severas para atraso em paradas `CRITICAL` ($+5.000$ + $4\times$ o tempo acumulado), sobrecarga de volume ($+10.000\text{/kg}$) e estouro de autonomia ($+2.000\text{/km}$)."

---

## Bloco 5: Projeto 2 — Demonstração Ao Vivo no Mapa Leaflet + IA Generativa Logística (11:00 – 13:45)

**Tela:** Navegador na aba `/routes` ([medical-routes.component.ts](file:///c:/GitHub/tech-challenge-health-ai/frontend/src/app/pages/medical-routes/medical-routes.component.ts)).

**Roteiro de Fala:**
> "Vamos ver o **Projeto 2 funcionando ao vivo** na interface `/routes`:
>
> 1. **Cenários Reais e Geocodificação Nominatim:**
>    Podemos carregar cenários hospitalares pré-configurados de **Salvador-BA (Hub HGE)** ou **São Paulo-SP (Hub HC-FMUSP)** com 15 hospitais e UPAs reais, ou ainda buscar qualquer endereço na barra superior integrada ao OpenStreetMap Nominatim (`/api/v1/routes/geocode`) ou clicar direto no mapa para adicionar um novo destino customizado definindo sua prioridade (`Crítico`, `Alto` ou `Regular`) e carga em quilos.
>
> 2. **Configuração da Frota e Execução do AG:**
>    *(Abrir o modal de Configuração de Frota e AG e clicar em 'Otimizar Rotas (AG)')*
>    Configuramos o número de veículos, capacidade máxima em kg, autonomia máxima em km e os hiperparâmetros do AG (População, Gerações e Taxa de Mutação). Ao executar a otimização, vemos o mapa Leaflet renderizar em cores distintas as polilinhas reais do OSRM para cada veículo, reduzindo a distância total em cerca de **32%** e o tempo em trânsito em **28%** frente ao roteamento manual, com **zero violações** de capacidade ou autonomia.
>
> 3. **Integração com LLM (`logistics_llm.py`) nas 4 Abas Operacionais:**
>    - Na **Aba 1 (Itinerário por Veículo)**, conferimos a sequência exata de paradas, horários estimados, distância e ocupação de carga de cada veículo.
>    - Na **Aba 2 (Instruções para Motoristas)**, clicamos para acionar o endpoint `/api/v1/routes/instructions`: o Gemini gera ordens de serviço passo a passo prontas para impressão ou envio via WhatsApp, destacando alertas de cadeia de frio ($2^\circ\text{C}$ a $8^\circ\text{C}$) para entregas críticas.
>    - Na **Aba 3 (Relatório Executivo)**, acionamos `/api/v1/routes/report`: a IA analisa as métricas da frota, identifica gargalos e calcula a economia estimada de combustível e de emissões de $\text{CO}_2$.
>    - Na **Aba 4 (Chat Logístico com IA)**, usamos `/api/v1/routes/chat` para fazer perguntas em linguagem natural sobre a operação — por exemplo: *'Qual veículo está com maior ocupação de carga e qual hospital crítico ele atende primeiro?'* — recebendo uma resposta contextualizada instantaneamente."

---

## Bloco 6: Testes Automatizados (`pytest`) e Conclusão (13:45 – 15:00)

**Tela:** Mostrar o terminal na pasta `backend/` executando `pytest -v`.

**Roteiro de Fala:**
> "Para garantir qualidade de engenharia de ponta a ponta, implementamos suítes de testes automatizados com `pytest`:
> - Em `tests/test_genetic_hyperopt.py`, validamos a codificação e decodificação de cromossomos, os operadores de seleção por torneio e roleta, o crossover híbrido, a mutação limitada e a convergência do otimizador evolucionário.
> - Em `tests/test_routing_vrp.py`, validamos o Order Crossover (OX) garantindo ausência de cidades duplicadas, a mutação 2-opt, a priorização clínica estrita (`CRITICAL` antes de `REGULAR`), o respeito à capacidade dos veículos e todos os endpoints FastAPI de rotas e LLM.
>
> Com isso, concluímos a apresentação da Fase 2 do Tech Challenge, unindo Algoritmos Genéticos clássicos e IA Generativa em uma plataforma médica completa, escalável e auditável. Muito obrigado!"
