"""
Camada de Cache Persistente de Rotas e Matrizes (P-020).
Utiliza SQLite local leve em backend/data/geo_cache.db para armazenar matrizes NxN
e polilinhas GeoJSON, garantindo velocidade imediata e consumo ZERO de requisições repetidas.
"""

import os
import sqlite3
import json
import hashlib
from typing import List, Dict, Any, Optional, Tuple

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data")
DB_PATH = os.path.join(DATA_DIR, "geo_cache.db")

class GeoCache:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS matrix_cache (
                    hash_key TEXT PRIMARY KEY,
                    num_points INTEGER,
                    durations_json TEXT,
                    distances_json TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS polyline_cache (
                    hash_key TEXT PRIMARY KEY,
                    geojson TEXT,
                    duration_sec REAL,
                    distance_m REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()

    @staticmethod
    def _compute_points_hash(points: List[Tuple[float, float]]) -> str:
        """
        Gera hash MD5 estável a partir de lista ordenada de (lat, lon) arredondadas.
        """
        key_str = "_".join(f"{round(lat, 5)},{round(lon, 5)}" for lat, lon in points)
        return hashlib.md5(key_str.encode("utf-8")).hexdigest()

    def get_matrix(self, points: List[Tuple[float, float]]) -> Optional[Tuple[List[List[float]], List[List[float]]]]:
        h = self._compute_points_hash(points)
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT durations_json, distances_json FROM matrix_cache WHERE hash_key = ?", (h,))
            row = cursor.fetchone()
            if row:
                return json.loads(row[0]), json.loads(row[1])
        return None

    def set_matrix(self, points: List[Tuple[float, float]], durations: List[List[float]], distances: List[List[float]]):
        h = self._compute_points_hash(points)
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO matrix_cache (hash_key, num_points, durations_json, distances_json)
                VALUES (?, ?, ?, ?)
            """, (h, len(points), json.dumps(durations), json.dumps(distances)))
            conn.commit()

    def get_polyline(self, waypoints: List[Tuple[float, float]]) -> Optional[Dict[str, Any]]:
        h = self._compute_points_hash(waypoints)
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT geojson, duration_sec, distance_m FROM polyline_cache WHERE hash_key = ?", (h,))
            row = cursor.fetchone()
            if row:
                return {
                    "geojson": json.loads(row[0]),
                    "duration_sec": row[1],
                    "distance_m": row[2]
                }
        return None

    def set_polyline(self, waypoints: List[Tuple[float, float]], geojson: Dict[str, Any], duration_sec: float, distance_m: float):
        h = self._compute_points_hash(waypoints)
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO polyline_cache (hash_key, geojson, duration_sec, distance_m)
                VALUES (?, ?, ?, ?)
            """, (h, json.dumps(geojson), duration_sec, distance_m))
            conn.commit()

geo_cache = GeoCache()
