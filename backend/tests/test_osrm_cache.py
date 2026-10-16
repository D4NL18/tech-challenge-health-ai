import os
import tempfile
import pytest
from app.services.geo.geo_cache import GeoCache
from app.services.geo.osrm_provider import OSRMProvider

def test_geo_cache_sqlite_persistence():
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        tmp_db = f.name
        
    try:
        cache = GeoCache(db_path=tmp_db)
        points = [(-23.55, -46.63), (-23.56, -46.64)]
        durations = [[0.0, 300.0], [300.0, 0.0]]
        distances = [[0.0, 2500.0], [2500.0, 0.0]]
        
        # Teste antes de salvar
        assert cache.get_matrix(points) is None
        
        # Salva
        cache.set_matrix(points, durations, distances)
        
        # Recupera
        cached = cache.get_matrix(points)
        assert cached is not None
        assert cached[0] == durations
        assert cached[1] == distances
    finally:
        try:
            if os.path.exists(tmp_db):
                os.remove(tmp_db)
        except Exception:
            pass

def test_osrm_provider_matrix_dimensions():
    provider = OSRMProvider()
    points = [
        (-23.5577, -46.6688),
        (-23.5599, -46.6489),
        (-23.5435, -46.6508)
    ]
    durations, distances = provider.get_matrix(points)
    assert len(durations) == 3
    assert len(durations[0]) == 3
    assert len(distances) == 3
    assert durations[0][0] == 0.0
