import pytest
from app.genetic.routing.traffic_model import TrafficPredictor, CityTier

def test_traffic_multiplier_city_tiers():
    # Salvador e São Paulo são metrópoles (Tier 1)
    tier_ssa = TrafficPredictor.get_city_tier("Salvador")
    assert tier_ssa == CityTier.METROPOLIS

    tier_sp = TrafficPredictor.get_city_tier("São Paulo")
    assert tier_sp == CityTier.METROPOLIS

    # Feira de Santana é polo regional (Tier 2)
    tier_fsa = TrafficPredictor.get_city_tier("Feira de Santana")
    assert tier_fsa == CityTier.REGIONAL_HUB

    # Mata de São João é cidade pequena / litoral (Tier 4)
    tier_msj = TrafficPredictor.get_city_tier("Mata de São João")
    assert tier_msj == CityTier.SMALL_TOWN

    # Alagoinhas é cidade média (Tier 3)
    tier_alg = TrafficPredictor.get_city_tier("Alagoinhas")
    assert tier_alg == CityTier.MEDIUM_CITY

def test_traffic_rush_hour_vs_offpeak():
    # Pico da Manhã às 08:15 (495 min) em Salvador
    k_morning, cond_morning = TrafficPredictor.get_traffic_multiplier(
        time_minutes_from_midnight=495.0,
        distance_km=10.0,
        origin_city="Salvador",
        dest_city="Salvador"
    )
    assert k_morning >= 1.60
    assert "PICO" in cond_morning

    # Entrepico às 11:00 (660 min) em Salvador
    k_offpeak, cond_offpeak = TrafficPredictor.get_traffic_multiplier(
        time_minutes_from_midnight=660.0,
        distance_km=10.0,
        origin_city="Salvador",
        dest_city="Salvador"
    )
    assert k_offpeak <= 1.10
    assert cond_offpeak == "LIVRE"

    # Pico da Tarde às 18:15 (1095 min) em São Paulo
    k_evening, cond_evening = TrafficPredictor.get_traffic_multiplier(
        time_minutes_from_midnight=1095.0,
        distance_km=8.0,
        origin_city="São Paulo",
        dest_city="São Paulo"
    )
    assert k_evening >= 1.65
    assert cond_evening == "PICO_TARDE"

def test_corridor_highway_attenuation():
    # Trecho rodoviário longo (> 20 km) na Linha Verde (Lauro de Freitas -> Guarajuba)
    k_hwy, cond_hwy = TrafficPredictor.get_traffic_multiplier(
        time_minutes_from_midnight=495.0, # 08:15
        distance_km=35.0,
        origin_city="Lauro de Freitas",
        dest_city="Guarajuba",
        base_city="Lauro de Freitas"
    )
    # Rodovia atenua o pico
    assert k_hwy < 1.45
    assert "RODOVIA" in cond_hwy

def test_time_parsing_and_formatting():
    mins = TrafficPredictor.parse_time_str("08:30")
    assert mins == 510.0

    clock = TrafficPredictor.format_clock(510.0)
    assert clock == "08:30"

    assert TrafficPredictor.parse_time_str(None) is None
    assert TrafficPredictor.format_clock(None) is None
