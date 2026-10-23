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

from app.genetic.routing.traffic_model import TrafficPredictor

# Schemas Pydantic
class LocationPoint(BaseModel):
    id: str
    name: str
    lat: float
    lon: float
    city: Optional[str] = Field("Salvador", description="Município ou cidade do ponto")

class DeliveryPoint(LocationPoint):
    demand: float = Field(10.0, description="Demanda em kg ou caixas térmicas (padrão neutro)")
    priority: str = Field("REGULAR", description="CRITICAL, HIGH ou REGULAR")
    critical_medication: bool = Field(False, description="Verdadeiro se exige transporte refrigerado urgente")
    assigned_vehicle: Optional[int] = Field(None, ge=1, le=10, description="Número da van/motorista vinculado (1 para Van 1, etc.) ou None para automático")
    service_duration_minutes: Optional[int] = Field(15, ge=0, description="Tempo estimado de permanência/descarregamento em minutos no hospital")

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
    departure_time: Optional[str] = Field("08:00", description="Horário planejado de saída da base (formato HH:MM)")
    default_service_minutes: Optional[int] = Field(15, ge=0, description="Tempo padrão em cada parada (minutos)")
    base_city: Optional[str] = Field("Salvador", description="Cidade base para contextualização de tráfego")

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

import unicodedata
import re
import urllib.request
import urllib.parse
import json

# Cache em memória para busca de endereços e geocodificação ultra-rápida (<1ms)
_geocode_cache: Dict[str, List[Dict[str, Any]]] = {}

def _normalize_search_text(text: str) -> str:
    """Remove acentos, pontuação e converte para minúsculas para busca robusta."""
    if not text:
        return ""
    nfkd = unicodedata.normalize("NFKD", text)
    no_acc = "".join(c for c in nfkd if not unicodedata.combining(c))
    return re.sub(r"[^a-zA-Z0-9\s]", " ", no_acc).lower().strip()

# Dicionário pré-indexado de POIs hospitalares e marcos em Salvador e São Paulo
PREINDEXED_LANDMARKS: List[Dict[str, Any]] = [
    # Salvador - Hospitais e Centros de Saúde
    {
        "name": "SENAI CIMATEC",
        "display_name": "SENAI CIMATEC, Avenida Orlando Gomes, Piatã, Salvador, Bahia, Brasil",
        "lat": -12.9352,
        "lon": -38.3619,
        "type": "university",
        "keywords": "senai cimatec piata tecnologia orlando gomes universidade centro pesquisa"
    },
    {
        "name": "Hospital Geral do Estado (HGE)",
        "display_name": "HGE - Hospital Geral do Estado da Bahia, Avenida Vasco da Gama, Brotas, Salvador, BA",
        "lat": -12.9984,
        "lon": -38.4908,
        "type": "hospital",
        "keywords": "hge hospital geral do estado vasco da gama brotas urgencia trauma"
    },
    {
        "name": "Hospital Universitário Edgard Santos (HUPES)",
        "display_name": "HUPES - Hospital das Clínicas da UFBA, Rua Augusto Viana, Canela, Salvador, BA",
        "lat": -12.9925,
        "lon": -38.5208,
        "type": "hospital",
        "keywords": "hupes hospital das clinicas ufba canela augusto viana universitario"
    },
    {
        "name": "Hospital Santo Antônio (Obras Irmã Dulce)",
        "display_name": "Hospital Santo Antônio - OSID, Avenida Bonfim, Roma / Cidade Baixa, Salvador, BA",
        "lat": -12.9328,
        "lon": -38.4975,
        "type": "hospital",
        "keywords": "irma dulce osid hospital santo antonio bonfim roma cidade baixa"
    },
    {
        "name": "Hospital Geral Roberto Santos (HGRS)",
        "display_name": "HGRS - Hospital Geral Roberto Santos, Estrada do Saboeiro, Cabula, Salvador, BA",
        "lat": -12.9567,
        "lon": -38.4552,
        "type": "hospital",
        "keywords": "roberto santos hgrs cabula saboeiro hospital publico"
    },
    {
        "name": "Hospital da Bahia",
        "display_name": "Hospital da Bahia, Avenida Professor Magalhães Neto, Pituba, Salvador, BA",
        "lat": -12.9912,
        "lon": -38.4523,
        "type": "hospital",
        "keywords": "hospital da bahia pituba magalhaes neto cardiologia"
    },
    {
        "name": "Hospital São Rafael",
        "display_name": "Hospital São Rafael - Rede D'Or, Avenida São Rafael, São Marcos, Salvador, BA",
        "lat": -12.9345,
        "lon": -38.4312,
        "type": "hospital",
        "keywords": "sao rafael rede d or sao marcos avenida sao rafael oncologia"
    },
    {
        "name": "Hospital Aliança",
        "display_name": "Hospital Aliança - Rede D'Or, Avenida Juracy Magalhães Júnior, Rio Vermelho, Salvador, BA",
        "lat": -12.9978,
        "lon": -38.4795,
        "type": "hospital",
        "keywords": "hospital alianca rede d or rio vermelho juracy magalhaes"
    },
    {
        "name": "Hospital Português",
        "display_name": "Real Sociedade Portuguesa de Beneficência (Hospital Português), Barra, Salvador, BA",
        "lat": -13.0031,
        "lon": -38.5256,
        "type": "hospital",
        "keywords": "hospital portugues barra princesa isabel gracia beneficencia"
    },
    {
        "name": "Hospital Mater Dei Salvador",
        "display_name": "Hospital Mater Dei Salvador, Avenida Vasco da Gama, Rio Vermelho, Salvador, BA",
        "lat": -13.0012,
        "lon": -38.4892,
        "type": "hospital",
        "keywords": "mater dei salvador vasco da gama rio vermelho hospital particular"
    },
    {
        "name": "Hospital Santa Izabel",
        "display_name": "Hospital Santa Izabel - Santa Casa da Bahia, Praça Almeida Couto, Nazaré, Salvador, BA",
        "lat": -12.9798,
        "lon": -38.5042,
        "type": "hospital",
        "keywords": "santa izabel santa casa nazare almeida couto cardiologia"
    },
    {
        "name": "Hospital Teresa de Lisieux",
        "display_name": "Hospital Teresa de Lisieux - Hapvida, Avenida Antônio Carlos Magalhães, Itaigara, Salvador, BA",
        "lat": -12.9875,
        "lon": -38.4682,
        "type": "hospital",
        "keywords": "teresa de lisieux hapvida acm antonio carlos magalhaes itaigara"
    },
    {
        "name": "Hospital Municipal de Salvador",
        "display_name": "Hospital Municipal de Salvador, Via Coletora B, Boca da Mata / Cajazeiras, Salvador, BA",
        "lat": -12.8987,
        "lon": -38.3982,
        "type": "hospital",
        "keywords": "hospital municipal boca da mata cajazeiras prefeitura salvador"
    },
    {
        "name": "UPA 24h Barris",
        "display_name": "UPA 24h Barris, Vale dos Barris, Centro, Salvador, BA",
        "lat": -12.9868,
        "lon": -38.5132,
        "type": "emergency",
        "keywords": "upa barris 24h vale dos barris centro pronto atendimento"
    },
    {
        "name": "UPA 24h Brotas",
        "display_name": "UPA 24h Brotas, Avenida Dom João VI, Brotas, Salvador, BA",
        "lat": -12.9834,
        "lon": -38.4876,
        "type": "emergency",
        "keywords": "upa brotas dom joao vi pronto atendimento 24 horas"
    },
    {
        "name": "UPA 24h Roma",
        "display_name": "UPA 24h Roma, Rua Fernandes da Cunha, Roma / Cidade Baixa, Salvador, BA",
        "lat": -12.9356,
        "lon": -38.4988,
        "type": "emergency",
        "keywords": "upa roma cidade baixa fernandes cunha pronto atendimento"
    },
    {
        "name": "UPA 24h San Martin",
        "display_name": "UPA 24h San Martin, Avenida General San Martin, Salvador, BA",
        "lat": -12.9512,
        "lon": -38.4891,
        "type": "emergency",
        "keywords": "upa san martin general san martin emergência 24h"
    },
    {
        "name": "UPA 24h Itapuã",
        "display_name": "UPA 24h Hélio Machado, Rua da Cacimba, Itapuã, Salvador, BA",
        "lat": -12.9389,
        "lon": -38.3582,
        "type": "emergency",
        "keywords": "upa itapua helio machado cacimba pronto socorro"
    },
    {
        "name": "Multicentro de Saúde Carlos Gomes",
        "display_name": "Multicentro de Saúde Carlos Gomes, Rua Carlos Gomes, Centro, Salvador, BA",
        "lat": -12.9812,
        "lon": -38.5145,
        "type": "clinic",
        "keywords": "multicentro carlos gomes centro policlinica ambulatorio"
    },
    {
        "name": "Centro de Saúde Liberdade",
        "display_name": "Centro de Saúde Nelson Piauhy Dourado, Estrada da Liberdade, Salvador, BA",
        "lat": -12.9482,
        "lon": -38.4921,
        "type": "clinic",
        "keywords": "centro de saude liberdade nelson piauhy posto de saude"
    },
    # Salvador - Bairros e Marcos Relevantes
    {
        "name": "Farol da Barra",
        "display_name": "Farol da Barra, Largo do Farol da Barra, Barra, Salvador, Bahia",
        "lat": -13.0101,
        "lon": -38.5327,
        "type": "landmark",
        "keywords": "barra farol da barra praia da barra largo do farol orla"
    },
    {
        "name": "Pelourinho (Centro Histórico)",
        "display_name": "Pelourinho - Centro Histórico de Salvador, Praça José de Alencar, Salvador, BA",
        "lat": -12.9714,
        "lon": -38.5081,
        "type": "neighborhood",
        "keywords": "pelourinho centro historico se carmo praca jose de alencar"
    },
    {
        "name": "Pituba",
        "display_name": "Bairro da Pituba, Avenida Manoel Dias da Silva, Salvador, BA",
        "lat": -13.0033,
        "lon": -38.4592,
        "type": "neighborhood",
        "keywords": "pituba manoel dias paulo vi orla pituba"
    },
    {
        "name": "Rio Vermelho",
        "display_name": "Largo de Santana, Rio Vermelho, Salvador, BA",
        "lat": -13.0135,
        "lon": -38.4923,
        "type": "neighborhood",
        "keywords": "rio vermelho dante paganelli acarajé santana paciencia"
    },
    {
        "name": "Ondina (Campus Universitário UFBA)",
        "display_name": "Campus Universitário de Ondina - UFBA, Avenida Adhemar de Barros, Ondina, Salvador, BA",
        "lat": -13.0015,
        "lon": -38.5085,
        "type": "university",
        "keywords": "ondina ufba adhemar de barros zoológico campus universitario"
    },
    {
        "name": "Estação da Lapa",
        "display_name": "Terminal da Lapa, Vale do Tororó / Piedade, Salvador, BA",
        "lat": -12.9808,
        "lon": -38.5112,
        "type": "station",
        "keywords": "lapa estacao da lapa terminal de onibus metro vale do tororo piedade"
    },
    {
        "name": "Dique do Tororó",
        "display_name": "Dique do Tororó, Avenida Vasco da Gama, Tororó, Salvador, BA",
        "lat": -12.9850,
        "lon": -38.5050,
        "type": "landmark",
        "keywords": "dique do tororo orixas arena fonte nova vasco da gama"
    },
    {
        "name": "Arena Fonte Nova",
        "display_name": "Complexo Esportivo Itaipava Arena Fonte Nova, Nazaré, Salvador, BA",
        "lat": -12.9788,
        "lon": -38.5042,
        "type": "stadium",
        "keywords": "arena fonte nova estadio bahia nazare dique"
    },
    {
        "name": "Itaigara",
        "display_name": "Bairro do Itaigara, Avenida ACM, Salvador, BA",
        "lat": -12.9930,
        "lon": -38.4680,
        "type": "neighborhood",
        "keywords": "itaigara shopping itaigara parque da cidade acm"
    },
    {
        "name": "Brotas",
        "display_name": "Bairro de Brotas, Avenida Dom João VI, Salvador, BA",
        "lat": -12.9850,
        "lon": -38.4850,
        "type": "neighborhood",
        "keywords": "brotas dom joao vi campinas de brotas vila laura"
    },
    # São Paulo - Hospitais e Marcos Demo
    {
        "name": "Hospital das Clínicas da FMUSP (Hub Central)",
        "display_name": "Hospital das Clínicas da FMUSP, Cerqueira César, São Paulo, SP",
        "lat": -23.5577,
        "lon": -46.6688,
        "type": "hospital",
        "keywords": "hospital das clinicas fmusp cerqueira cesar dr arnaldo sao paulo hc"
    },
    {
        "name": "Santa Casa de São Paulo",
        "display_name": "Irmandade da Santa Casa de Misericórdia de São Paulo, Santa Cecília, SP",
        "lat": -23.5435,
        "lon": -46.6508,
        "type": "hospital",
        "keywords": "santa casa de sao paulo santa cecilia cesario motta misericordia"
    },
    {
        "name": "Hospital São Paulo (UNIFESP)",
        "display_name": "Hospital São Paulo - Escola Paulista de Medicina (UNIFESP), Vila Clementino, SP",
        "lat": -23.5975,
        "lon": -46.6432,
        "type": "hospital",
        "keywords": "hospital sao paulo unifesp epm vila clementino napoleao de barros"
    },
    {
        "name": "Hospital Sírio-Libanês",
        "display_name": "Hospital Sírio-Libanês, Rua Dona Adma Jafet, Bela Vista, São Paulo, SP",
        "lat": -23.5578,
        "lon": -46.6542,
        "type": "hospital",
        "keywords": "sirio libanes bela vista adma jafet hospital particular sp"
    },
    {
        "name": "Hospital Israelita Albert Einstein",
        "display_name": "Hospital Israelita Albert Einstein, Morumbi, São Paulo, SP",
        "lat": -23.5998,
        "lon": -46.7153,
        "type": "hospital",
        "keywords": "albert einstein morumbi israelita hospital sao paulo"
    },
    {
        "name": "Avenida Paulista",
        "display_name": "Avenida Paulista, Bela Vista / Cerqueira César, São Paulo, SP",
        "lat": -23.5614,
        "lon": -46.6565,
        "type": "landmark",
        "keywords": "avenida paulista masp trianon consolação brigadeiro"
    }
]

def _search_preindexed_landmarks(query: str, limit: int = 6) -> List[Dict[str, Any]]:
    """Busca ultra-rápida em memória nos pontos de interesse com ranking por relevância."""
    norm_q = _normalize_search_text(query)
    if not norm_q or len(norm_q) < 2:
        return []

    tokens = norm_q.split()
    scored_matches = []

    for item in PREINDEXED_LANDMARKS:
        norm_name = _normalize_search_text(item["name"])
        norm_disp = _normalize_search_text(item["display_name"])
        norm_keys = _normalize_search_text(item.get("keywords", ""))
        full_haystack = f"{norm_name} {norm_disp} {norm_keys}"

        score = 0
        # Correspondência exata no nome
        if norm_q == norm_name:
            score += 100
        elif norm_name.startswith(norm_q):
            score += 50
        elif norm_q in norm_name:
            score += 35

        # Verificação dos tokens individuais
        matched_tokens = 0
        for token in tokens:
            if len(token) >= 2 and token in full_haystack:
                matched_tokens += 1
                if token in norm_name:
                    score += 15
                elif token in norm_keys:
                    score += 10
                else:
                    score += 5

        if matched_tokens == len(tokens) or score >= 20:
            score += matched_tokens * 10
            scored_matches.append((score, {
                "name": item["name"],
                "display_name": item["display_name"],
                "lat": item["lat"],
                "lon": item["lon"],
                "type": item["type"]
            }))

    # Ordena pelo maior score
    scored_matches.sort(key=lambda x: x[0], reverse=True)
    return [match[1] for match in scored_matches[:limit]]

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
    Busca endereços de alta performance (<1ms para POIs indexados ou com cache; fallback inteligente Nominatim).
    Retorna coordenadas e descrições para navegação do mapa.
    """
    query = q.strip()
    norm_key = _normalize_search_text(query)
    if not norm_key:
        return []

    # 1. Hit imediato no Cache em Memória L1
    if norm_key in _geocode_cache:
        return _geocode_cache[norm_key]

    # 2. Busca nos POIs pré-indexados de Salvador e SP (Instantâneo, <1ms)
    local_matches = _search_preindexed_landmarks(query, limit=6)
    if local_matches:
        _geocode_cache[norm_key] = local_matches
        return local_matches

    # 3. Fallback online Nominatim com timeout curto (2.0s) para não travar a UI
    search_term = query if "salvador" in query.lower() or "brasil" in query.lower() else f"{query}, Salvador, Bahia"
    encoded_q = urllib.parse.quote(search_term)
    url = f"https://nominatim.openstreetmap.org/search?format=json&q={encoded_q}&countrycodes=br&limit=6&addressdetails=1"

    results = []
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "HealthAI-Salvador-VRP/2.0 (Academic Research; FIAP)"}
        )
        with urllib.request.urlopen(req, timeout=2.0) as response:
            if response.status == 200:
                raw_data = json.loads(response.read().decode("utf-8"))
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
    except Exception as e:
        # Timeout ou erro transitório de rede Nominatim
        pass

    # Se a busca restrita não achou, faz busca mais aberta rápida
    if not results:
        try:
            encoded_fallback = urllib.parse.quote(query)
            url_fb = f"https://nominatim.openstreetmap.org/search?format=json&q={encoded_fallback}&countrycodes=br&limit=6"
            req_fb = urllib.request.Request(url_fb, headers={"User-Agent": "HealthAI-Salvador-VRP/2.0"})
            with urllib.request.urlopen(req_fb, timeout=1.8) as resp_fb:
                if resp_fb.status == 200:
                    raw_data = json.loads(resp_fb.read().decode("utf-8"))
                    results = [
                        {
                            "name": item.get("name") or item.get("display_name", "").split(",")[0].strip(),
                            "display_name": item.get("display_name"),
                            "lat": float(item.get("lat")),
                            "lon": float(item.get("lon")),
                            "type": item.get("type", "address")
                        }
                        for item in raw_data
                    ]
        except Exception:
            pass

    # Se ainda assim não achou nada externo, retorna as recomendações mais relevantes de Salvador
    if not results:
        results = [
            {
                "name": item["name"],
                "display_name": item["display_name"],
                "lat": item["lat"],
                "lon": item["lon"],
                "type": item["type"]
            }
            for item in PREINDEXED_LANDMARKS[:4]
        ]

    _geocode_cache[norm_key] = results
    return results


@router.post("/optimize")
def optimize_routes(payload: OptimizeRoutesRequest):
    """
    Executa a otimização de rotas pelo Algoritmo Genético sobre a malha viária OSRM,
    incorporando trânsito dinâmico por horário de pico, horário planejado de partida
    e estimativa de tempo em cada parada médica (dwell time).
    """
    if not payload.deliveries:
        raise HTTPException(status_code=400, detail="É necessário fornecer ao menos uma entrega.")

    # Extração de Horário de Partida e Contexto Urbano
    dep_time_mins = TrafficPredictor.parse_time_str(payload.departure_time)
    if dep_time_mins is None:
        dep_time_mins = 480.0 # 08:00 por padrão
    departure_clock_str = TrafficPredictor.format_clock(dep_time_mins) or "08:00"

    base_city = payload.base_city or payload.depot.city or "Salvador"

    # Monta a lista completa de pontos e cidades: [Depósito (0)] + [Entregas (1..N)]
    all_points = [(payload.depot.lat, payload.depot.lon)] + [
        (d.lat, d.lon) for d in payload.deliveries
    ]
    points_cities = [base_city]
    for d in payload.deliveries:
        points_cities.append(d.city or base_city)

    # 1. Obtém matriz de distâncias e tempos via OSRM (Batch único protegido por cache SQLite)
    durations_sec, distances_m = osrm_provider.get_matrix(all_points)

    # 2. Executa o Algoritmo Genético VRP em RAM com suporte a Trânsito Dinâmico
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
        mutation_rate=payload.ga_params.mutation_rate,
        departure_time_minutes=dep_time_mins,
        default_service_minutes=payload.default_service_minutes or 15,
        base_city=base_city,
        points_cities=points_cities
    )
    result = solver.solve()

    # 3. Monta os objetos de resposta enriquecidos com GeoJSON, relógio e status de trânsito
    routes_response = []
    total_time_min = 0.0
    total_transit_min = 0.0
    total_service_min = 0.0
    total_dist_km = 0.0
    all_peak_count = 0
    van_finish_clocks_min = []

    for v_idx, route_indices in enumerate(result["routes_by_vehicle"]):
        if not route_indices:
            continue

        stops = []
        waypoints_for_geo = []
        route_transit_sec = 0.0
        route_service_min = 0.0
        route_dist_m = 0.0
        curr_clock_min = dep_time_mins

        all_urgency_finish_sec = []
        for step_num, node_idx in enumerate(route_indices):
            if step_num == 0:
                # Partida da Base Central
                stops.append({
                    "step": 0,
                    "name": payload.depot.name,
                    "lat": payload.depot.lat,
                    "lon": payload.depot.lon,
                    "action": "DEPARTURE",
                    "critical": False,
                    "demand": 0,
                    "arrival_time_minutes": 0.0,
                    "estimated_arrival_clock": departure_clock_str,
                    "estimated_departure_clock": departure_clock_str,
                    "service_duration_minutes": 0,
                    "traffic_factor": 1.0,
                    "traffic_condition": "LIVRE"
                })
                waypoints_for_geo.append((payload.depot.lat, payload.depot.lon))
            else:
                prev_idx = route_indices[step_num - 1]
                leg_dist_m = distances_m[prev_idx][node_idx]
                leg_dist_km = leg_dist_m / 1000.0
                base_sec = durations_sec[prev_idx][node_idx]

                orig_city = points_cities[prev_idx] if prev_idx < len(points_cities) else base_city
                dest_city = points_cities[node_idx] if node_idx < len(points_cities) else base_city

                traffic_k, traffic_cond = TrafficPredictor.get_traffic_multiplier(
                    time_minutes_from_midnight=curr_clock_min,
                    distance_km=leg_dist_km,
                    origin_city=orig_city,
                    dest_city=dest_city,
                    base_city=base_city
                )
                if "PICO" in traffic_cond:
                    all_peak_count += 1

                adjusted_leg_sec = base_sec * traffic_k
                route_transit_sec += adjusted_leg_sec
                route_dist_m += leg_dist_m

                if curr_clock_min is not None:
                    curr_clock_min += (adjusted_leg_sec / 60.0)

                arrival_clock_str = TrafficPredictor.format_clock(curr_clock_min)
                accumulated_transit_min = round(route_transit_sec / 60.0, 1)

                if node_idx == 0:
                    # Retorno à Base Central
                    stops.append({
                        "step": step_num,
                        "name": payload.depot.name,
                        "lat": payload.depot.lat,
                        "lon": payload.depot.lon,
                        "action": "RETURN",
                        "critical": False,
                        "demand": 0,
                        "arrival_time_minutes": accumulated_transit_min,
                        "estimated_arrival_clock": arrival_clock_str,
                        "estimated_departure_clock": arrival_clock_str,
                        "service_duration_minutes": 0,
                        "traffic_factor": traffic_k,
                        "traffic_condition": traffic_cond
                    })
                    waypoints_for_geo.append((payload.depot.lat, payload.depot.lon))
                else:
                    deliv = payload.deliveries[node_idx - 1]
                    prio_str = str(deliv.priority).upper()
                    is_crit = prio_str in ("CRITICAL", "IMMEDIATE") or deliv.critical_medication
                    is_urgent = is_crit or prio_str in ("HIGH", "URGENT")
                    if is_urgent:
                        all_urgency_finish_sec.append(route_transit_sec)

                    stop_service = deliv.service_duration_minutes if (deliv.service_duration_minutes is not None and deliv.service_duration_minutes >= 0) else (payload.default_service_minutes or 15)
                    route_service_min += stop_service

                    if curr_clock_min is not None:
                        curr_clock_min += stop_service
                    departure_from_stop_clock = TrafficPredictor.format_clock(curr_clock_min)

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
                        "arrival_time_minutes": accumulated_transit_min,
                        "estimated_arrival_clock": arrival_clock_str,
                        "estimated_departure_clock": departure_from_stop_clock,
                        "service_duration_minutes": stop_service,
                        "traffic_factor": traffic_k,
                        "traffic_condition": traffic_cond
                    })
                    waypoints_for_geo.append((deliv.lat, deliv.lon))

        # Obtém a geometria curva a curva via OSRM para desenho no mapa Leaflet
        geojson = osrm_provider.get_route_geometry(waypoints_for_geo)

        v_transit_min = round(route_transit_sec / 60.0, 1)
        v_total_min = round(v_transit_min + route_service_min, 1)
        v_dist_km = round(route_dist_m / 1000.0, 1)

        total_time_min += v_total_min
        total_transit_min += v_transit_min
        total_service_min += route_service_min
        total_dist_km += v_dist_km
        if curr_clock_min is not None:
            van_finish_clocks_min.append(curr_clock_min)

        routes_response.append({
            "vehicle_id": v_idx + 1,
            "stops": stops,
            "route_time_minutes": v_total_min,
            "route_transit_minutes": v_transit_min,
            "route_service_minutes": route_service_min,
            "route_distance_km": v_dist_km,
            "geojson_geometry": geojson
        })

    urgency_makespan_min = round(max(all_urgency_finish_sec) / 60.0, 1) if all_urgency_finish_sec else 0.0
    vehicles_count = len(routes_response) if routes_response else 1
    avg_time_min = round(total_time_min / vehicles_count, 1)
    avg_dist_km = round(total_dist_km / vehicles_count, 1)

    latest_finish_min = max(van_finish_clocks_min) if van_finish_clocks_min else dep_time_mins
    estimated_finish_clock = TrafficPredictor.format_clock(latest_finish_min)

    summary = {
        "total_time_minutes": round(total_time_min, 1),
        "total_distance_km": round(total_dist_km, 1),
        "average_time_minutes": avg_time_min,
        "average_distance_km": avg_dist_km,
        "vehicles_used": len(routes_response),
        "total_deliveries": len(payload.deliveries),
        "urgency_makespan_minutes": urgency_makespan_min,
        "departure_clock": departure_clock_str,
        "estimated_finish_clock": estimated_finish_clock,
        "total_transit_minutes": round(total_transit_min, 1),
        "total_service_minutes": round(total_service_min, 1),
        "peak_hours_encountered": all_peak_count,
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
