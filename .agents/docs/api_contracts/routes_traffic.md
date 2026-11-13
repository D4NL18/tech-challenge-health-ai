# Contrato de API REST: Otimização de Rotas com Cálculo de Trânsito Dinâmico

> **Localização Mandatória:** `.agents/docs/api_contracts/routes_traffic.md`  
> **Responsável:** Arquiteto (`api-contract-expert`)  
> **Regras Vinculadas:** P-030 a P-034  

---

## 1. Visão Geral
- **Prefixo da Rota:** `/api/v1/routes`
- **Protocolo:** HTTP/REST
- **Formato:** `application/json`

---

## 2. Endpoints Atualizados

### 2.1. `POST /api/v1/routes/optimize`
- **Objetivo:** Otimizar as rotas do VRP hospitalar com AG sobre malha OSRM incorporando trânsito dinâmico por horário de pico, horário de partida e tempo em paradas.

#### Request Body (`OptimizeRoutesRequest`):
```json
{
  "depot": {
    "id": "hub-salvador-hge",
    "name": "Hospital Geral do Estado (HGE)",
    "lat": -12.9984,
    "lon": -38.4908,
    "city": "Salvador"
  },
  "deliveries": [
    {
      "id": "del-ssa-1",
      "name": "Hospital Universitário Edgard Santos",
      "lat": -12.9925,
      "lon": -38.5208,
      "demand": 25.0,
      "priority": "CRITICAL",
      "critical_medication": true,
      "assigned_vehicle": null,
      "service_duration_minutes": 15,
      "city": "Salvador"
    }
  ],
  "fleet": {
    "num_vehicles": 2,
    "capacity_per_vehicle": 110.0,
    "max_distance_km": 100.0
  },
  "ga_params": {
    "population_size": 40,
    "generations": 25,
    "mutation_rate": 0.20
  },
  "departure_time": "08:00",
  "default_service_minutes": 15,
  "base_city": "Salvador"
}
```

#### Response Body (`OptimizeRoutesResponse`):
```json
{
  "success": true,
  "summary": {
    "total_time_minutes": 98.4,
    "total_distance_km": 34.2,
    "average_time_minutes": 49.2,
    "average_distance_km": 17.1,
    "vehicles_used": 2,
    "total_deliveries": 9,
    "urgency_makespan_minutes": 22.5,
    "departure_clock": "08:00",
    "estimated_finish_clock": "09:38",
    "total_transit_minutes": 68.4,
    "total_service_minutes": 30.0,
    "peak_hours_encountered": 4,
    "elapsed_seconds": 0.32
  },
  "routes": [
    {
      "vehicle_id": 1,
      "route_time_minutes": 48.5,
      "route_distance_km": 16.8,
      "stops": [
        {
          "step": 0,
          "name": "Hospital Geral do Estado (HGE)",
          "lat": -12.9984,
          "lon": -38.4908,
          "action": "DEPARTURE",
          "critical": false,
          "demand": 0,
          "arrival_time_minutes": 0.0,
          "estimated_arrival_clock": "08:00",
          "estimated_departure_clock": "08:00",
          "service_duration_minutes": 0,
          "traffic_factor": 1.0,
          "traffic_condition": "LIVRE"
        },
        {
          "step": 1,
          "name": "Hospital Universitário Edgard Santos",
          "lat": -12.9925,
          "lon": -38.5208,
          "action": "DELIVERY",
          "critical": true,
          "priority": "CRITICAL",
          "demand": 25.0,
          "assigned_vehicle": null,
          "arrival_time_minutes": 14.2,
          "estimated_arrival_clock": "08:14",
          "estimated_departure_clock": "08:29",
          "service_duration_minutes": 15,
          "traffic_factor": 1.68,
          "traffic_condition": "PICO_MANHA"
        }
      ],
      "geojson_geometry": {}
    }
  ],
  "fitness_history": [120.4, 105.2, 98.4]
}
```
