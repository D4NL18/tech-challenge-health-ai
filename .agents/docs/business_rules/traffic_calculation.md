# Regras de Negócio: Cálculo de Trânsito Dinâmico por Porte de Cidade, Horário de Partida e Tempo em Paradas (P-030 a P-034)

> **Localização Mandatória:** `.agents/docs/business_rules/traffic_calculation.md`  
> **Responsável:** Analista & Arquiteto (`business-rules-expert` / `architect`)  
> **Origem / Referência:** `fitoherb-ai` (Módulo `traffic_model.py` e Regras de Roteirização Comercial)

---

## 1. Contexto e Objetivo
- **User Story:** Como gestor de logística médica hospitalar, desejo que o cálculo de rotas considere o horário de saída das vans da base, o tempo de permanência/descarregamento em cada hospital/UPA e o trânsito real dinâmico baseado no tamanho da cidade e nos horários de pico, para que a previsão de chegada seja fidedigna e as entregas críticas não sofram atrasos imprevisíveis causados por congestionamentos urbanos.
- **Atores Envolvidos:** Central de Regulação Hospitalar, Farmacêuticos Hospitalares, Motoristas de Transporte Refrigerado.

---

## 2. Catálogo de Regras de Negócio (P-030 a P-034)

### `P-030`: Classificação Hierárquica por Porte Urbano (`CityTier`)
- **Declaração Mandatória:** O sistema DEVE classificar os municípios em 4 portes (`CityTier`):
  1. `METROPOLIS`: População > 1 milhão ou capitais metropolitanas (ex: Salvador, São Paulo, Rio de Janeiro, Belo Horizonte, Curitiba, etc.).
  2. `REGIONAL_HUB`: Polos regionais com 300k a 1M habitantes (ex: Feira de Santana, Lauro de Freitas, Camaçari, Campinas, Santos).
  3. `MEDIUM_CITY`: Cidades médias com 100k a 300k habitantes (ex: Alagoinhas, Simões Filho, Ilhéus, Jequié).
  4. `SMALL_TOWN`: Cidades menores ou interior/litoral com < 100k habitantes (ex: Mata de São João, Pojuca).
- **Condições de Ativação:** Em qualquer cálculo de trecho viário entre duas localidades (origem e destino).
- **Resultado Esperado:** Se qualquer uma das pontas do trecho for `METROPOLIS`, o multiplicador de trânsito adotado para a perna é o de `METROPOLIS`. Caso contrário, prevalece o maior nível de urbanização entre as cidades do trecho ou o contexto da cidade base (`base_city`, padrão: `Salvador`).

### `P-031`: Multiplicador Contínuo por Faixa Horária e Horários de Pico
- **Declaração Mandatória:** O sistema DEVE aplicar uma função contínua de intensidade de tráfego $k(\tau)$ ao tempo nominal do grafo OSRM baseada no relógio em minutos desde meia-noite ($\tau \in [0, 1440)$):
  - **Pico da Manhã (07:00 a 09:30 / 420 a 570 min):** Ápice às 08:15 (495 min).
  - **Pico do Almoço (12:00 a 13:30 / 720 a 810 min):** Ápice às 12:45 (765 min).
  - **Pico da Tarde/Noite (17:00 a 19:30 / 1020 a 1170 min):** Ápice às 18:15 (1095 min).
  - **Madrugada (22:00 a 06:00):** Fluxo 100% livre ($k = 1.00$).
- **Multiplicadores Máximos por Porte:**
  - `METROPOLIS`: Pico Manhã `1.70`, Pico Almoço `1.25`, Pico Tarde `1.75`, Fora de Pico `1.05`.
  - `REGIONAL_HUB`: Pico Manhã `1.45`, Pico Almoço `1.18`, Pico Tarde `1.48`, Fora de Pico `1.05`.
  - `MEDIUM_CITY`: Pico Manhã `1.25`, Pico Almoço `1.10`, Pico Tarde `1.28`, Fora de Pico `1.02`.
  - `SMALL_TOWN`: Pico Manhã `1.10`, Pico Almoço `1.05`, Pico Tarde `1.12`, Fora de Pico `1.00`.
- **Interpolação:** A intensidade é suavizada linearmente em relação à distância do ápice do pico.

### `P-032`: Atenuação para Trechos Rodoviários Longos (> 20 km)
- **Declaração Mandatória:** Em trechos rodoviários interurbanos com distância viária superior a 20.0 km, o sistema DEVE atenuar o impacto do congestionamento urbano, reduzindo o excesso de lentidão em 40%:
  $$\text{se } d > 20\text{ km e } k > 1.15 \implies k_{\text{ajustado}} = 1.0 + ((k - 1.0) \times 0.60)$$
- **Condição:** Status descritivo alterado para `MODERADO_RODOVIA`.

### `P-033`: Propagação Cronológica de Partida e Tempo em Paradas (Dwell Time)
- **Declaração Mandatória:** O itinerário DEVE propagar o relógio de forma cumulativa em tempo real:
  1. A van parte da Base no horário programado (`departure_time`, padrão: `08:00`).
  2. Cada deslocamento consome $t_{\text{viagem}} = \text{duracao\_osrm} \times k(\tau)$.
  3. No ponto de chegada, o horário de previsão de chegada é registrado (`estimated_arrival_clock`).
  4. A van permanece no hospital/UPA pelo tempo de atendimento (`service_duration_minutes`, padrão: 15 minutos).
  5. O horário de partida do hospital é registrado (`estimated_departure_clock`).
  6. A perna seguinte é avaliada sob o novo horário do relógio, sujeita às condições de trânsito daquele instante.

### `P-034`: Transparência e Métricas de Tráfego no Retorno da API e UI
- **Declaração Mandatória:** Cada parada no itinerário retornado DEVE conter:
  - `estimated_arrival_clock`: Horário projetado de chegada no relógio (formato `HH:MM`).
  - `estimated_departure_clock`: Horário projetado de saída após atendimento (formato `HH:MM`).
  - `service_duration_minutes`: Tempo de atendimento alocado nesta parada.
  - `traffic_factor`: Multiplicador viário aplicado no trecho de chegada (ex: `1.68`).
  - `traffic_condition`: Status semântico do tráfego (`LIVRE`, `MODERADO`, `PICO_MANHA`, `PICO_ALMOCO`, `PICO_TARDE`, `MODERADO_RODOVIA`).
- O resumo da otimização DEVE quantificar o `total_transit_minutes`, `total_service_minutes` e `peak_hours_encountered`.
