"""
Router de Otimização de Rotas Hospitalares (VRP com OSRM e LLM - Fase 2).
Exponibiliza endpoints REST para cálculo de rotas com restrições médicas,
cenário de demonstração, geração de instruções ao motorista, relatórios e chat.
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from app.services.geo.osrm_provider import osrm_provider
from app.genetic.routing.vrp_solver import VRPSolver
from app.services.logistics_llm import logistics_llm_service

router = APIRouter(
    prefix="/api/v1/routes",
    tags=["Rotas e Logística Hospitalar (VRP)"]
)

# Schemas Pydantic
class LocationPoint(BaseModel):
    id: str
    name: str
    lat: float
    lon: float

class DeliveryPoint(LocationPoint):
    demand: float = Field(10.0, description="Demanda em kg ou caixas térmicas (padrão neutro)")
    priority: str = Field("REGULAR", description="CRITICAL, HIGH ou REGULAR")
    critical_medication: bool = Field(False, description="Verdadeiro se exige transporte refrigerado urgente")
    assigned_vehicle: Optional[int] = Field(None, ge=1, le=10, description="Número da van/motorista vinculado (1 para Van 1, etc.) ou None para automático")

class FleetConfig(BaseModel):
    num_vehicles: int = Field(2, ge=1, le=10)
    capacity_per_vehicle: float = Field(80.0, ge=10.0)
    max_distance_km: float = Field(120.0, ge=10.0)

class GAParameters(BaseModel):
    population_size: int = Field(50, ge=10, le=200)
    generations: int = Field(30, ge=5, le=100)
    mutation_rate: float = Field(0.20, ge=0.01, le=0.50)

class OptimizeRoutesRequest(BaseModel):
    depot: LocationPoint
    deliveries: List[DeliveryPoint]
    fleet: FleetConfig = FleetConfig()
    ga_params: GAParameters = GAParameters()

class DriverInstructionsRequest(BaseModel):
    vehicle_id: int
    stops: List[Dict[str, Any]]
    total_time_min: float
    total_distance_km: float

class EfficiencyReportRequest(BaseModel):
    summary: Dict[str, Any]
    routes: List[Dict[str, Any]]

class ChatRequest(BaseModel):
    question: str
    context: Dict[str, Any]

# Cenário de demonstração realista em São Paulo
DEMO_SCENARIO = {
    "depot": {
        "id": "hc-central",
        "name": "Hospital das Clínicas da FMUSP (Hub Central)",
        "lat": -23.5577,
        "lon": -46.6688
    },
    "deliveries": [
        {
            "id": "del-1",
            "name": "UBS Bela Vista",
            "lat": -23.5599,
            "lon": -46.6489,
            "demand": 25.0,
            "priority": "HIGH",
            "critical_medication": True
        },
        {
            "id": "del-2",
            "name": "Santa Casa de São Paulo",
            "lat": -23.5435,
            "lon": -46.6508,
            "demand": 30.0,
            "priority": "HIGH",
            "critical_medication": True
        },
        {
            "id": "del-3",
            "name": "UBS Santa Cecília",
            "lat": -23.5358,
            "lon": -46.6542,
            "demand": 15.0,
            "priority": "REGULAR",
            "critical_medication": False
        },
        {
            "id": "del-4",
            "name": "UBS Cerqueira César",
            "lat": -23.5645,
            "lon": -46.6675,
            "demand": 20.0,
            "priority": "REGULAR",
            "critical_medication": False
        },
        {
            "id": "del-5",
            "name": "Hospital São Paulo (UNIFESP)",
            "lat": -23.5975,
            "lon": -46.6432,
            "demand": 35.0,
            "priority": "HIGH",
            "critical_medication": True
        },
        {
            "id": "del-6",
            "name": "UBS Vila Mariana",
            "lat": -23.5852,
            "lon": -46.6389,
            "demand": 15.0,
            "priority": "REGULAR",
            "critical_medication": False
        },
        {
            "id": "del-7",
            "name": "UBS Consolação",
            "lat": -23.5489,
            "lon": -46.6534,
            "demand": 18.0,
            "priority": "REGULAR",
            "critical_medication": False
        },
        {
            "id": "del-8",
            "name": "UBS Perdizes",
            "lat": -23.5362,
            "lon": -46.6789,
            "demand": 22.0,
            "priority": "REGULAR",
            "critical_medication": False
        },
        {
            "id": "del-9",
            "name": "UBS Pinheiros",
            "lat": -23.5678,
            "lon": -46.6923,
            "demand": 20.0,
            "priority": "REGULAR",
            "critical_medication": False
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
    }
}

DEMO_SCENARIO_SALVADOR = {
    "depot": {
        "id": "hub-salvador-hge",
        "name": "Hospital Geral do Estado da Bahia (HGE - Hub Salvador)",
        "lat": -12.9984,
        "lon": -38.4908
    },
    "deliveries": [
        {
            "id": "del-ssa-1",
            "name": "Hospital Universitário Edgard Santos (HUPES - Canela)",
            "lat": -12.9925,
            "lon": -38.5208,
            "demand": 25.0,
            "priority": "CRITICAL",
            "critical_medication": True
        },
        {
            "id": "del-ssa-2",
            "name": "Hospital Santo Antônio - Obras Irmã Dulce (Roma)",
            "lat": -12.9328,
            "lon": -38.4975,
            "demand": 30.0,
            "priority": "CRITICAL",
            "critical_medication": True
        },
        {
            "id": "del-ssa-3",
            "name": "Hospital Geral Roberto Santos - HGRS (Cabula)",
            "lat": -12.9567,
            "lon": -38.4552,
            "demand": 20.0,
            "priority": "HIGH",
            "critical_medication": False
        },
        {
            "id": "del-ssa-4",
            "name": "Hospital da Bahia (Pituba)",
            "lat": -12.9912,
            "lon": -38.4523,
            "demand": 15.0,
            "priority": "REGULAR",
            "critical_medication": False
        },
        {
            "id": "del-ssa-5",
            "name": "UPA 24h Barris (Centro / Vale dos Barris)",
            "lat": -12.9868,
            "lon": -38.5132,
            "demand": 18.0,
            "priority": "REGULAR",
            "critical_medication": False
        },
        {
            "id": "del-ssa-6",
            "name": "Hospital São Rafael (São Marcos)",
            "lat": -12.9345,
            "lon": -38.4312,
            "demand": 22.0,
            "priority": "HIGH",
            "critical_medication": False
        },
        {
            "id": "del-ssa-7",
            "name": "UPA 24h Brotas",
            "lat": -12.9834,
            "lon": -38.4876,
            "demand": 12.0,
            "priority": "REGULAR",
            "critical_medication": False
        },
        {
            "id": "del-ssa-8",
            "name": "Multicentro de Saúde Carlos Gomes (Centro)",
            "lat": -12.9812,
            "lon": -38.5145,
            "demand": 16.0,
            "priority": "REGULAR",
            "critical_medication": False
        },
        {
            "id": "del-ssa-9",
            "name": "Hospital Municipal de Salvador (Boca da Mata)",
            "lat": -12.8987,
            "lon": -38.3982,
            "demand": 20.0,
            "priority": "REGULAR",
            "critical_medication": False
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
    }
}

@router.get("/demo-scenario")
def get_demo_scenario(city: str = Query("salvador", description="salvador ou sp")):
    """
    Retorna cenário médico realista de distribuição hospitalar (Salvador por padrão ou SP).
    """
    if city.lower() == "sp" or city.lower() == "saopaulo":
        return DEMO_SCENARIO
    return DEMO_SCENARIO_SALVADOR

@router.get("/geocode")
def geocode_address(q: str = Query(..., min_length=2)):
    """
    Busca endereços usando o serviço OpenStreetMap Nominatim.
    Retorna coordenadas e descrições para navegação do mapa.
    """
    import urllib.request
    import urllib.parse
    import json

    query = q.strip()
    # Se a busca não tiver menção a estado/país, adiciona contexto do Brasil
    search_term = query if "salvador" in query.lower() or "brasil" in query.lower() else f"{query}, Salvador, Bahia"
    encoded_q = urllib.parse.quote(search_term)
    url = f"https://nominatim.openstreetmap.org/search?format=json&q={encoded_q}&countrycodes=br&limit=6&addressdetails=1"

    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "HealthAI-Salvador-VRP/2.0 (Academic Research; FIAP)"}
        )
        with urllib.request.urlopen(req, timeout=5) as response:
            if response.status == 200:
                raw_data = json.loads(response.read().decode("utf-8"))
                results = []
                for item in raw_data:
                    display_parts = item.get("display_name", "").split(",")
                    short_name = item.get("name") or display_parts[0]
                    results.append({
                        "name": short_name.strip(),
                        "display_name": item.get("display_name"),
                        "lat": float(item.get("lat")),
                        "lon": float(item.get("lon")),
                        "type": item.get("type", "address")
                    })
                if results:
                    return results
    except Exception as e:
        print(f"[Geocode Primary Error] {e}")

    # Fallback de busca mais aberta se a restrita a Salvador não retornar
    try:
        encoded_fallback = urllib.parse.quote(query)
        url_fb = f"https://nominatim.openstreetmap.org/search?format=json&q={encoded_fallback}&countrycodes=br&limit=6"
        req_fb = urllib.request.Request(url_fb, headers={"User-Agent": "HealthAI-Salvador-VRP/2.0"})
        with urllib.request.urlopen(req_fb, timeout=5) as resp_fb:
            if resp_fb.status == 200:
                raw_data = json.loads(resp_fb.read().decode("utf-8"))
                return [
                    {
                        "name": item.get("name") or item.get("display_name", "").split(",")[0].strip(),
                        "display_name": item.get("display_name"),
                        "lat": float(item.get("lat")),
                        "lon": float(item.get("lon")),
                        "type": item.get("type", "address")
                    }
                    for item in raw_data
                ]
    except Exception as e:
        print(f"[Geocode Fallback Error] {e}")

    return []


@router.post("/optimize")
def optimize_routes(payload: OptimizeRoutesRequest):
    """
    Executa a otimização de rotas pelo Algoritmo Genético sobre a malha viária OSRM.
    """
    if not payload.deliveries:
        raise HTTPException(status_code=400, detail="É necessário fornecer ao menos uma entrega.")

    # Monta a lista completa de pontos: [Depósito (0)] + [Entregas (1..N)]
    all_points = [(payload.depot.lat, payload.depot.lon)] + [
        (d.lat, d.lon) for d in payload.deliveries
    ]

    # 1. Obtém matriz de distâncias e tempos via OSRM (Batch único protegido por cache SQLite)
    durations_sec, distances_m = osrm_provider.get_matrix(all_points)

    # 2. Executa o Algoritmo Genético VRP em RAM
    deliveries_dict = [d.model_dump() for d in payload.deliveries]
    solver = VRPSolver(
        durations_matrix_sec=durations_sec,
        distances_matrix_m=distances_m,
        deliveries_data=deliveries_dict,
        num_vehicles=payload.fleet.num_vehicles,
        capacity_per_vehicle=payload.fleet.capacity_per_vehicle,
        max_distance_km_per_vehicle=payload.fleet.max_distance_km,
        population_size=payload.ga_params.population_size,
        generations=payload.ga_params.generations,
        mutation_rate=payload.ga_params.mutation_rate
    )
    result = solver.solve()

    # 3. Monta os objetos de resposta enriquecidos com GeoJSON e paradas
    routes_response = []
    total_time_min = 0.0
    total_dist_km = 0.0

    for v_idx, route_indices in enumerate(result["routes_by_vehicle"]):
        if not route_indices:
            continue

        stops = []
        waypoints_for_geo = []
        route_time_sec = 0.0
        route_dist_m = 0.0

        all_urgency_finish_sec = []
        for step_num, node_idx in enumerate(route_indices):
            if step_num > 0:
                prev_idx = route_indices[step_num - 1]
                route_time_sec += durations_sec[prev_idx][node_idx]
                route_dist_m += distances_m[prev_idx][node_idx]

            arrival_min = round(route_time_sec / 60.0, 1)

            if node_idx == 0:
                is_departure = (step_num == 0)
                stops.append({
                    "step": step_num,
                    "name": payload.depot.name,
                    "lat": payload.depot.lat,
                    "lon": payload.depot.lon,
                    "action": "DEPARTURE" if is_departure else "RETURN",
                    "critical": False,
                    "demand": 0,
                    "arrival_time_minutes": arrival_min
                })
                waypoints_for_geo.append((payload.depot.lat, payload.depot.lon))
            else:
                deliv = payload.deliveries[node_idx - 1]
                prio_str = str(deliv.priority).upper()
                is_crit = prio_str in ("CRITICAL", "IMMEDIATE") or deliv.critical_medication
                is_urgent = is_crit or prio_str in ("HIGH", "URGENT")
                if is_urgent:
                    all_urgency_finish_sec.append(route_time_sec)

                stops.append({
                    "step": step_num,
                    "name": deliv.name,
                    "lat": deliv.lat,
                    "lon": deliv.lon,
                    "action": "DELIVERY",
                    "critical": is_crit,
                    "priority": prio_str,
                    "demand": deliv.demand,
                    "assigned_vehicle": deliv.assigned_vehicle,
                    "arrival_time_minutes": arrival_min
                })
                waypoints_for_geo.append((deliv.lat, deliv.lon))

        # Obtém a geometria curva a curva via OSRM para desenho no mapa Leaflet
        geojson = osrm_provider.get_route_geometry(waypoints_for_geo)

        v_time_min = round(route_time_sec / 60.0, 1)
        v_dist_km = round(route_dist_m / 1000.0, 1)
        total_time_min += v_time_min
        total_dist_km += v_dist_km

        routes_response.append({
            "vehicle_id": v_idx + 1,
            "stops": stops,
            "route_time_minutes": v_time_min,
            "route_distance_km": v_dist_km,
            "geojson_geometry": geojson
        })

    urgency_makespan_min = round(max(all_urgency_finish_sec) / 60.0, 1) if all_urgency_finish_sec else 0.0
    vehicles_count = len(routes_response) if routes_response else 1
    avg_time_min = round(total_time_min / vehicles_count, 1)
    avg_dist_km = round(total_dist_km / vehicles_count, 1)

    summary = {
        "total_time_minutes": round(total_time_min, 1),
        "total_distance_km": round(total_dist_km, 1),
        "average_time_minutes": avg_time_min,
        "average_distance_km": avg_dist_km,
        "vehicles_used": len(routes_response),
        "total_deliveries": len(payload.deliveries),
        "urgency_makespan_minutes": urgency_makespan_min,
        "elapsed_seconds": result["elapsed_seconds"]
    }

    return {
        "success": True,
        "summary": summary,
        "routes": routes_response,
        "fitness_history": result["fitness_history"]
    }

@router.post("/instructions")
def get_driver_instructions(payload: DriverInstructionsRequest):
    """
    Gera instruções e roteiro detalhado para o motorista com apoio de LLM.
    """
    text = logistics_llm_service.generate_driver_instructions(
        vehicle_id=payload.vehicle_id,
        stops=payload.stops,
        total_time_min=payload.total_time_min,
        total_distance_km=payload.total_distance_km
    )
    return {"instructions": text}

@router.post("/report")
def get_efficiency_report(payload: EfficiencyReportRequest):
    """
    Gera relatório executivo de eficiência operacional com apoio de LLM.
    """
    text = logistics_llm_service.generate_efficiency_report(
        summary=payload.summary,
        routes_data=payload.routes
    )
    return {"report": text}

@router.post("/chat")
def chat_routes(payload: ChatRequest):
    """
    Responde em linguagem natural a perguntas sobre as rotas e veículos.
    """
    answer = logistics_llm_service.chat_about_routes(
        question=payload.question,
        context=payload.context
    )
    return {"answer": answer}
