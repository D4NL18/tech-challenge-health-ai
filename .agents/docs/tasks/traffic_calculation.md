# Entidade / Feature: Cálculo Dinâmico de Trânsito no VRP Hospitalar

Este documento centraliza todo o planejamento, as especificações e as etapas de execução para a implementação do cálculo de trânsito baseado em **horário de partida**, **tempo de parada** e **tamanho da cidade**, espelhado da implementação de referência em `github/fitoherb-ai`.

---

## 1. Dúvidas Resolvidas (Especificação)
- **Dúvida:** Como o cálculo de trânsito em `fitoherb-ai` modela os horários de pico e tamanho de cidades?
  - **Decisão:** Utiliza o `TrafficPredictor` e `CityTier` com 4 categorias (`METROPOLIS`, `REGIONAL_HUB`, `MEDIUM_CITY`, `SMALL_TOWN`). Modela 3 picos diários (Manhã 07:00-09:30 com ápice 08:15; Almoço 12:00-13:30 com ápice 12:45; Tarde 17:00-19:30 com ápice 18:15; e madrugada 22:00-06:00 livre). Além disso, aplica atenuação de 40% em rodovias (> 20 km) e interpolação contínua de intensidade.
- **Dúvida:** Como o horário de partida e a estimativa de tempo em cada parada afetam o cálculo?
  - **Decisão:** A van parte da Base no `departure_time` (ex: "08:00"). Cada deslocamento acumula tempo ajustado por trânsito no relógio (`curr_clock_min += adjusted_leg_sec / 60.0`). Ao chegar no ponto, registra `estimated_arrival_clock`. Permanece pelo tempo de atendimento (`service_duration_minutes`, ex: 15 min), acumulando no relógio (`curr_clock_min += service_min`), e registra `estimated_departure_clock`. A perna seguinte é calculada sob as condições de trânsito daquele novo horário.
- **Dúvida:** Como o Algoritmo Genético VRP (Multi-Van) deve usar esse trânsito?
  - **Decisão:** O avaliador de fitness (`routing_fitness.py`) deve avaliar cada perna da rota de cada van com o multiplicador de trânsito dinâmico em função do relógio daquela van, garantindo que o makespan de urgências e as rotas totais reflitam a realidade de congestionamento e tempos em paradas.

---

## 2. Tarefas e Etapas de Desenvolvimento

### Tarefa 1: Criação do Módulo `TrafficPredictor` e `CityTier` no Backend
**Descritivo Detalhado:**
Criar `backend/app/genetic/routing/traffic_model.py` idêntico à modelagem do `fitoherb-ai`, incluindo suporte a Salvador, São Paulo e cidades da Bahia/Brasil, parsing de horários e formatação de relógio.

**Critérios de Aceite:**
- [ ] Retornar `CityTier.METROPOLIS` para Salvador e São Paulo.
- [ ] Calcular multiplicador de pico da manhã de até 1.70 para Salvador.
- [ ] Atenuar trechos > 20 km em 40% do excesso.
- [ ] Testes unitários dedicados em `backend/tests/test_traffic_model.py` passando com 100%.

**Checklist Técnico:**
- [ ] Criar `backend/app/genetic/routing/traffic_model.py`.
- [ ] Criar `backend/tests/test_traffic_model.py` com testes para tiers, picos, rodovia e formatação de relógio.

---

### Tarefa 2: Integração com o Fitness Evaluator e Solver do VRP
**Descritivo Detalhado:**
Atualizar `backend/app/genetic/routing/routing_fitness.py` e `vrp_solver.py` para receber `departure_time_minutes`, `default_service_minutes`, `base_city` e lista de cidades das paradas.

**Critérios de Aceite:**
- [ ] O fitness e tempo total das rotas calculam o tempo real com trânsito e dwell times.
- [ ] Manter e respeitar o balanceamento das 3 prioridades clínicas (Crítica, Alta, Regular).
- [ ] Testes unitários do VRP atualizados e 100% aprovados.

**Checklist Técnico:**
- [ ] Adicionar método `_calculate_leg_transit(...)` no `VRPFitnessEvaluator`.
- [ ] Propagar `curr_clock_min` e dwell time em cada van individualmente durante a avaliação das rotas.
- [ ] Atualizar parâmetros do construtor e chamadas no `VRPSolver`.

---

### Tarefa 3: Atualização dos Schemas Pydantic e Endpoint REST
**Descritivo Detalhado:**
Atualizar `backend/app/api/routers/routes_router.py` para suportar `departure_time`, `default_service_minutes`, `service_duration_minutes` por ponto, `city`, e enriquecer os `stops` e `summary` da resposta com horários do relógio, fatores de trânsito e contagem de picos.

**Critérios de Aceite:**
- [ ] `POST /api/v1/routes/optimize` aceita `departure_time` e `default_service_minutes`.
- [ ] Retorna `estimated_arrival_clock`, `estimated_departure_clock`, `traffic_factor`, `traffic_condition` em cada etapa de cada van.
- [ ] Resumo inclui `departure_clock`, `total_transit_minutes`, `total_service_minutes`, `peak_hours_encountered`.
- [ ] Testes de API em `backend/tests/test_routes_api.py` aprovados.

---

### Tarefa 4: Atualização do Frontend Angular (Tipos, Controles e Visualização)
**Descritivo Detalhado:**
Atualizar `routes.service.ts`, `medical-routes.component.ts` e `medical-routes.component.html` para permitir:
1. Configurar Horário de Partida da Base (ex: "08:00") e Duração Padrão por Parada (ex: 15 min).
2. Configurar no Modal de Parada o tempo de atendimento individual do hospital.
3. Exibir no Itinerário os badges de trânsito (ex: 🚦 1.68x Pico Manhã), horários de chegada/saída e métricas consolidadas de trânsito vs atendimento.

**Critérios de Aceite:**
- [ ] Usuário pode visualizar e ajustar o horário de partida e tempo em paradas.
- [ ] Cada card da timeline exibe a previsão de chegada no relógio (HH:MM), previsão de saída e tag de trânsito com cores semânticas.
- [ ] Build do Angular executado sem erros.

---

### Tarefa 5: Validação End-to-End e Execução do Projeto
**Descritivo Detalhado:**
Executar a suíte de testes completa do pytest, verificar o build do Angular, rodar o backend FastAPI e frontend Angular e demonstrar o funcionamento pleno do sistema com trânsito dinâmico.
