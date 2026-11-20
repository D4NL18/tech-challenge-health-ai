# Regras de Negócio: Otimização de Rotas Médicas (TSP/VRP) com OSRM e LLM

> **Localização Mandatória:** `.agents/docs/business_rules/BR-020-roteamento-medico-tsp-vrp.md`  
> **Responsável:** Analista (`business-rules-expert`)  
> **User Stories:** US-09, US-10, US-11, US-12

---

## 1. Contexto e Objetivo
- **User Story Relacionada:** US-09 a US-12 (Fase 2 - Projeto 2).
- **Objetivo da Feature:** Otimizar o roteamento de frotas de distribuição de medicamentos e insumos hospitalares (VRP) utilizando Algoritmos Genéticos sobre malha de mapas reais com grafos ponderados por tempo (OSRM/OpenStreetMap), com restrições operacionais realistas e instruções por LLM.
- **Atores Envolvidos:** Gestor de Logística Hospitalar, Motorista/Entregador, Sistema de Roteamento.

---

## 2. Catálogo de Regras de Negócio (P-020 a P-029)

### `P-020`: Consulta em Batch Único de Matriz de Tempos (Anti-Esgotamento)
- **Declaração Mandatória:** O sistema DEVE consultar o provedor de mapas (OSRM) para obtenção da matriz $N \times N$ de tempos e distâncias em exatamente **1 única requisição HTTP em lote (*batch*)** antes do início da evolução genética, persistindo o resultado no cache SQLite local (`backend/data/geo_cache.db`).
- **Condições de Ativação:** Ao receber uma solicitação de otimização para $N$ coordenadas.
- **Resultado Esperado:** O loop do Algoritmo Genético executa 100% em memória RAM em microssegundos com zero requisições externas de rede.

### `P-021`: Restrição de Medicamentos Críticos (Prioridade Máxima)
- **Declaração Mandatória:** O sistema DEVE penalizar severamente na função fitness qualquer indivíduo que posicione paradas com medicamentos de urgência/críticos em etapas tardias da jornada de entrega ou que ultrapassem janelas de segurança temporal.
- **Resultado Esperado:** As entregas urgentes aparecem priorizadas nas primeiras posições de cada itinerário gerado.

### `P-022`: Restrição de Capacidade de Carga do Veículo
- **Declaração Mandatória:** A soma das demandas (kg ou caixas térmicas) de todos os pontos atribuídos a um veículo NÃO DEVE exceder a capacidade máxima do veículo. Caso exceda, uma penalidade proporcional é somada ao fitness do cromossomo.
- **Resultado Esperado:** Divisão equilibrada da carga entre os veículos disponíveis.

### `P-023`: Restrição de Autonomia Máxima da Frota
- **Declaração Mandatória:** A distância total percorrida por um veículo NÃO DEVE ultrapassar o limite de autonomia cadastrado (ex: 150 km por veículo). Violações sofrem penalidade no fitness.

### `P-024`: Operadores Genéticos Livres de Duplicidade (OX / PMX)
- **Declaração Mandatória:** Os operadores de crossover do VRP DEVEM obrigatoriamente ser baseados em permutação válida (Order Crossover - OX ou Partially Mapped Crossover - PMX), garantindo que cada ponto de entrega seja visitado exatamente uma vez por um único veículo.

### `P-025`: Geração de Itinerário e Relatório Logístico por LLM
- **Declaração Mandatória:** O sistema DEVE transformar as rotas numéricas (sequência de coordenadas e tempos de viagem) em: (1) Roteiro passo a passo humanizado para os motoristas com avisos de cuidados térmicos; (2) Relatório executivo de eficiência (tempo economizado, km totais, taxa de atendimento); (3) Assistente interativo capaz de responder dúvidas pontuais em linguagem natural.

---

## 3. Critérios de Aceitação (DoD)
- [x] OSRM em lote com cache SQLite verificado.
- [x] Testes unitários com crossover OX e mutação 2-opt.
- [x] Visualização no mapa Leaflet e rota `/routes` ativa no frontend.
