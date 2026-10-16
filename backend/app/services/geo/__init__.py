"""
Módulo de Serviços de Geolocalização e Grafos de Mapas (Fase 2).
"""
from .geo_cache import geo_cache, GeoCache
from .osrm_provider import osrm_provider, OSRMProvider

__all__ = ["geo_cache", "GeoCache", "osrm_provider", "OSRMProvider"]
