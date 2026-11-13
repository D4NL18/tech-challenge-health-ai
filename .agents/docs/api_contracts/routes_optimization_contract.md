# Contrato de API: Otimização de Rotas Médicas (VRP com OSRM e LLM)

> **Localização Mandatória:** `.agents/docs/api_contracts/routes_optimization_contract.md`  
> **Responsável:** Arquiteto (`api-contract-expert`)  
> **Versão da API:** `v1`  
> **Base Path:** `/api/v1/routes`

---

## 1. Endpoints

### 1.1 `POST /api/v1/routes/optimize`
Otimiza as rotas de entrega de medicamentos hospitalares entre múltiplos pontos e veículos via Algoritmo Genético e OSRM.

**Headers:**
- `Content-Type: application/json`

**Request Body Schema:**
```json
{
  "depot": {
    "id": "hub-central",
    "name": "Hospital das Clínicas - Hub Central",
    "lat": -23.5577,
    "lon": -46.6688
  },
  "deliveries": [
    {
      "id": "del-1",
      "name": "UBS Bela Vista",
      "lat": -23.5599,
      "lon": -46.6489,
      "demand": 15.0,
      "priority": "HIGH",
      "critical_medication": true
    }
  ],
  "fleet": {
    "num_vehicles": 2,
    "capacity_per_vehicle": 80.0,
    "max_distance_km": 120.0
  },
  "ga_params": {
    "population_size": 50,
    "generations": 30,
    "mutation_rate": 0.15
  }
}
```

**Response 200 OK Schema:**
```json
{
  "success": true,
  "summary": {
    "total_time_minutes": 84.5,
    "total_distance_km": 38.2,
    "vehicles_used": 2,
    "critical_deliveries_served_first": true
  },
  "routes": [
    {
      "vehicle_id": 1,
      "stops": [
        { "step": 0, "name": "Hospital das Clínicas - Hub Central", "action": "DEPARTURE" },
        { "step": 1, "name": "UBS Bela Vista", "action": "DELIVERY", "critical": true }
      ],
      "route_time_minutes": 42.0,
      "route_distance_km": 18.5,
      "geojson_geometry": { "type": "LineString", "coordinates": [[-46.6688, -23.5577], [-46.6489, -23.5599]] }
    }
  ],
  "fitness_history": [145.2, 120.4, 98.1, 84.5]
}
```

---

### 1.2 `GET /api/v1/routes/demo-scenario`
Retorna um cenário pré-configurado e realista de São Paulo para testes e demonstração imediata no frontend.

---

### 1.3 `POST /api/v1/routes/instructions`
Gera roteiro passo a passo com instruções humanizadas para os motoristas via LLM.

---

### 1.4 `POST /api/v1/routes/report`
Gera relatório executivo de eficiência logística e economia de tempo via LLM.

---

### 1.5 `POST /api/v1/routes/chat`
Assistente em linguagem natural para perguntas e respostas sobre o status das rotas e veículos.
