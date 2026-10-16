import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_routes_demo_scenario_endpoint():
    response = client.get("/api/v1/routes/demo-scenario")
    assert response.status_code == 200
    data = response.json()
    assert "depot" in data
    assert "deliveries" in data
    assert len(data["deliveries"]) >= 5

def test_routes_optimize_endpoint():
    payload = {
        "depot": {"id": "hc", "name": "Hub Central", "lat": -23.5577, "lon": -46.6688},
        "deliveries": [
            {"id": "d1", "name": "UBS 1", "lat": -23.5599, "lon": -46.6489, "demand": 20.0, "priority": "HIGH", "critical_medication": True},
            {"id": "d2", "name": "UBS 2", "lat": -23.5435, "lon": -46.6508, "demand": 15.0, "priority": "REGULAR", "critical_medication": False},
            {"id": "d3", "name": "UBS 3", "lat": -23.5358, "lon": -46.6542, "demand": 10.0, "priority": "REGULAR", "critical_medication": False}
        ],
        "fleet": {"num_vehicles": 2, "capacity_per_vehicle": 50.0, "max_distance_km": 100.0},
        "ga_params": {"population_size": 15, "generations": 5, "mutation_rate": 0.20}
    }
    response = client.post("/api/v1/routes/optimize", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "summary" in data
    assert "routes" in data
    assert len(data["routes"]) >= 1

def test_routes_instructions_and_report_endpoints():
    inst_payload = {
        "vehicle_id": 1,
        "stops": [
            {"step": 0, "name": "Hub", "action": "DEPARTURE", "critical": False, "demand": 0},
            {"step": 1, "name": "UBS 1", "action": "DELIVERY", "critical": True, "demand": 15}
        ],
        "total_time_min": 35.0,
        "total_distance_km": 12.5
    }
    res_inst = client.post("/api/v1/routes/instructions", json=inst_payload)
    assert res_inst.status_code == 200
    assert "instructions" in res_inst.json()
    assert len(res_inst.json()["instructions"]) > 20

    rep_payload = {
        "summary": {"total_time_minutes": 55.0, "total_distance_km": 24.0, "vehicles_used": 2},
        "routes": []
    }
    res_rep = client.post("/api/v1/routes/report", json=rep_payload)
    assert res_rep.status_code == 200
    assert "report" in res_rep.json()

def test_explain_diagnosis_endpoint():
    payload = {
        "disease": "cancer",
        "patient_name": "Maria Silva",
        "patient_age": 48,
        "confidence_score": 0.85,
        "tabular_data": {"concavity_mean": 0.32, "radius_mean": 18.2}
    }
    response = client.post("/api/v1/anamnesis/explain-diagnosis", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "clinical_report" in data
    assert "key_risk_factors" in data["clinical_report"]
    assert "recommendations" in data["clinical_report"]
