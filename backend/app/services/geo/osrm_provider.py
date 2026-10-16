"""
Provedor de Roteamento OSRM / OpenStreetMap (P-020).
100% Gratuito, sem chaves de API, com grafos reais ponderados por tempo viário.
Inclui fallback com cálculo geodésico Haversine + velocidade média para resiliência offline total.
"""

import json
import math
import urllib.request
import urllib.parse
from typing import List, Tuple, Dict, Any
from .geo_cache import geo_cache

class OSRMProvider:
    BASE_URL = "https://router.project-osrm.org"

    @staticmethod
    def _haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calcula distância do grande círculo em km."""
        R = 6371.0
        phi1, phi2 = math.radians(lat1), math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlambda = math.radians(lon2 - lon1)
        a = math.sin(dphi / 2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2)**2
        return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    def get_matrix(self, points: List[Tuple[float, float]]) -> Tuple[List[List[float]], List[List[float]]]:
        """
        Retorna (durations_segundos, distances_metros) para todos os N pontos.
        Verifica o cache SQLite primeiro; se não houver, consulta o OSRM em 1 requisição batch.
        """
        cached = geo_cache.get_matrix(points)
        if cached:
            return cached

        # Formato OSRM: lon,lat;lon,lat
        coord_str = ";".join(f"{lon:.6f},{lat:.6f}" for lat, lon in points)
        url = f"{self.BASE_URL}/table/v1/driving/{coord_str}?annotations=duration,distance"

        try:
            req = urllib.request.Request(
                url, 
                headers={"User-Agent": "HealthAI-VRP-Hospital/2.0 (Academic Research; FIAP)"}
            )
            with urllib.request.urlopen(req, timeout=10) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode("utf-8"))
                    if data.get("code") == "Ok":
                        durations = data["durations"] # segundos
                        distances = data["distances"] # metros
                        geo_cache.set_matrix(points, durations, distances)
                        return durations, distances
        except Exception as e:
            print(f"[OSRMProvider] Falha de rede no OSRM ({e}). Acionando estimativa geodésica viária de alta precisão.")

        # Fallback offline resiliente: Matriz baseada em Haversine com fator de sinuosidade urbana (1.35) e velocidade média de 35 km/h
        n = len(points)
        durations = [[0.0] * n for _ in range(n)]
        distances = [[0.0] * n for _ in range(n)]

        for i in range(n):
            for j in range(n):
                if i != j:
                    lat1, lon1 = points[i]
                    lat2, lon2 = points[j]
                    dist_km = self._haversine_distance_km(lat1, lon1, lat2, lon2) * 1.35
                    dist_m = dist_km * 1000.0
                    duration_sec = (dist_km / 35.0) * 3600.0 # 35 km/h urbana
                    distances[i][j] = round(dist_m, 1)
                    durations[i][j] = round(duration_sec, 1)

        geo_cache.set_matrix(points, durations, distances)
        return durations, distances

    def get_route_geometry(self, waypoints: List[Tuple[float, float]]) -> Dict[str, Any]:
        """
        Retorna o GeoJSON completo com polilinhas e curvas para visualização no mapa Leaflet.
        """
        if len(waypoints) < 2:
            return {"type": "LineString", "coordinates": []}

        cached = geo_cache.get_polyline(waypoints)
        if cached:
            return cached["geojson"]

        coord_str = ";".join(f"{lon:.6f},{lat:.6f}" for lat, lon in waypoints)
        url = f"{self.BASE_URL}/route/v1/driving/{coord_str}?overview=full&geometries=geojson"

        try:
            req = urllib.request.Request(
                url, 
                headers={"User-Agent": "HealthAI-VRP-Hospital/2.0 (Academic Research; FIAP)"}
            )
            with urllib.request.urlopen(req, timeout=10) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode("utf-8"))
                    if data.get("code") == "Ok" and len(data.get("routes", [])) > 0:
                        route = data["routes"][0]
                        geojson = route["geometry"]
                        duration = route.get("duration", 0)
                        distance = route.get("distance", 0)
                        geo_cache.set_polyline(waypoints, geojson, duration, distance)
                        return geojson
        except Exception as e:
            print(f"[OSRMProvider] Falha ao obter polilinha no OSRM ({e}). Gerando GeoJSON linear.")

        # Fallback offline para linha reta entre os pontos
        fallback_geojson = {
            "type": "LineString",
            "coordinates": [[lon, lat] for lat, lon in waypoints]
        }
        geo_cache.set_polyline(waypoints, fallback_geojson, 0, 0)
        return fallback_geojson

osrm_provider = OSRMProvider()
