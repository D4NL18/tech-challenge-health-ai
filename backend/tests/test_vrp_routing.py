import pytest
from app.genetic.routing.vrp_chromosome import VRPChromosome
from app.genetic.routing.routing_operators import RoutingOperators
from app.genetic.routing.routing_fitness import VRPFitnessEvaluator
from app.genetic.routing.vrp_solver import VRPSolver

def test_vrp_chromosome_and_operators():
    num_deliveries = 8
    p1 = VRPChromosome.random(num_deliveries)
    p2 = VRPChromosome.random(num_deliveries)
    
    assert len(p1.sequence) == num_deliveries
    assert set(p1.sequence) == set(range(1, num_deliveries + 1))
    
    # Teste de Order Crossover (OX)
    c1, c2 = RoutingOperators.order_crossover_ox(p1, p2, pc=1.0)
    assert len(c1.sequence) == num_deliveries
    assert set(c1.sequence) == set(range(1, num_deliveries + 1)), "OX produziu duplicidade ou perda de nós!"
    assert set(c2.sequence) == set(range(1, num_deliveries + 1)), "OX produziu duplicidade ou perda de nós!"
    
    # Teste de Mutação
    mut = RoutingOperators.mutate(p1, pm=1.0)
    assert set(mut.sequence) == set(range(1, num_deliveries + 1)), "Mutação corrompeu os nós!"

def test_vrp_fitness_and_solver():
    # 4 nós: 0 (depósito), 1, 2, 3
    durations = [
        [0, 600, 1200, 900],
        [600, 0, 800, 500],
        [1200, 800, 0, 700],
        [900, 500, 700, 0]
    ]
    distances = [
        [0, 5000, 10000, 7000],
        [5000, 0, 6000, 4000],
        [10000, 6000, 0, 5000],
        [7000, 4000, 5000, 0]
    ]
    deliveries = [
        {"id": "1", "name": "UBS 1", "demand": 20, "critical_medication": True},
        {"id": "2", "name": "UBS 2", "demand": 30, "critical_medication": False},
        {"id": "3", "name": "UBS 3", "demand": 25, "critical_medication": True}
    ]

    solver = VRPSolver(
        durations_matrix_sec=durations,
        distances_matrix_m=distances,
        deliveries_data=deliveries,
        num_vehicles=2,
        capacity_per_vehicle=50,
        population_size=15,
        generations=10
    )
    res = solver.solve()
    assert res["best_fitness"] > 0
    assert len(res["routes_by_vehicle"]) == 2
    assert len(res["fitness_history"]) >= 10

def test_vrp_urgency_distribution_and_makespan():
    # Depósito (0) + 4 entregas: 1 e 2 no setor Leste, 3 e 4 no setor Oeste
    # Nós 1, 2, 3, 4 são urgências críticas
    durations = [
        [0, 400, 450, 420, 460],     # 0
        [400, 0, 100, 900, 950],     # 1 (Leste)
        [450, 100, 0, 920, 960],     # 2 (Leste)
        [420, 900, 920, 0, 120],     # 3 (Oeste)
        [460, 950, 960, 120, 0]      # 4 (Oeste)
    ]
    distances = [[d * 10 for d in row] for row in durations]
    deliveries = [
        {"id": "1", "name": "Leste A", "demand": 10, "critical_medication": True},
        {"id": "2", "name": "Leste B", "demand": 10, "critical_medication": True},
        {"id": "3", "name": "Oeste A", "demand": 10, "critical_medication": True},
        {"id": "4", "name": "Oeste B", "demand": 10, "critical_medication": True}
    ]

    solver = VRPSolver(
        durations_matrix_sec=durations,
        distances_matrix_m=distances,
        deliveries_data=deliveries,
        num_vehicles=2,
        capacity_per_vehicle=50,
        population_size=20,
        generations=15
    )
    res = solver.solve()
    routes = res["routes_by_vehicle"]
    assert len(routes) == 2
    # Cada van deve ter recebido nós urgentes para dividir a carga e minimizar o makespan
    van1_deliveries = [n for n in routes[0] if n > 0]
    van2_deliveries = [n for n in routes[1] if n > 0]
    assert len(van1_deliveries) == 2, f"Van 1 deveria ter recebido 2 nós, mas recebeu {van1_deliveries}"
    assert len(van2_deliveries) == 2, f"Van 2 deveria ter recebido 2 nós, mas recebeu {van2_deliveries}"
    # Deve agrupar por setor (1 e 2 juntos, 3 e 4 juntos)
    assert set(van1_deliveries) in [{1, 2}, {3, 4}]
    assert set(van2_deliveries) in [{1, 2}, {3, 4}]

def test_vrp_strict_vehicle_assignment():
    durations = [
        [0, 500, 600, 700],
        [500, 0, 300, 400],
        [600, 300, 0, 350],
        [700, 400, 350, 0]
    ]
    distances = [[d * 10 for d in row] for row in durations]
    # Ponto 3 fixado estritamente para Van 2
    deliveries = [
        {"id": "1", "name": "UBS 1", "demand": 10, "critical_medication": False},
        {"id": "2", "name": "UBS 2", "demand": 10, "critical_medication": False},
        {"id": "3", "name": "UBS 3 - Dedicado Van 2", "demand": 10, "critical_medication": False, "assigned_vehicle": 2}
    ]

    solver = VRPSolver(
        durations_matrix_sec=durations,
        distances_matrix_m=distances,
        deliveries_data=deliveries,
        num_vehicles=2,
        capacity_per_vehicle=50,
        population_size=15,
        generations=10
    )
    res = solver.solve()
    routes = res["routes_by_vehicle"]
    assert 3 in routes[1], f"Ponto 3 deveria estar estritamente na Van 2 (índice 1), mas routes={routes}"
    assert 3 not in routes[0]

def test_vrp_balanced_priority_distribution():
    # 2 veículos, 4 urgências (2 CRITICAL + 2 HIGH) e 4 REGULAR
    # Matriz sintética com 9 nós (0 = depósito)
    num_nodes = 9
    durations = [[abs(i - j) * 200 + (100 if i != j else 0) for j in range(num_nodes)] for i in range(num_nodes)]
    distances = [[d * 10 for d in row] for row in durations]

    deliveries = [
        {"id": "1", "name": "Critico 1", "demand": 10, "priority": "CRITICAL", "critical_medication": True},
        {"id": "2", "name": "Critico 2", "demand": 10, "priority": "CRITICAL", "critical_medication": True},
        {"id": "3", "name": "Alto 1", "demand": 10, "priority": "HIGH", "critical_medication": False},
        {"id": "4", "name": "Alto 2", "demand": 10, "priority": "HIGH", "critical_medication": False},
        {"id": "5", "name": "Regular 1", "demand": 10, "priority": "REGULAR", "critical_medication": False},
        {"id": "6", "name": "Regular 2", "demand": 10, "priority": "REGULAR", "critical_medication": False},
        {"id": "7", "name": "Regular 3", "demand": 10, "priority": "REGULAR", "critical_medication": False},
        {"id": "8", "name": "Regular 4", "demand": 10, "priority": "REGULAR", "critical_medication": False},
    ]

    solver = VRPSolver(
        durations_matrix_sec=durations,
        distances_matrix_m=distances,
        deliveries_data=deliveries,
        num_vehicles=2,
        capacity_per_vehicle=80,
        population_size=30,
        generations=20
    )
    res = solver.solve()
    routes = res["routes_by_vehicle"]
    assert len(routes) == 2

    # Verifica nós em cada van (ignorando depósito 0)
    van1 = [n for n in routes[0] if n > 0]
    van2 = [n for n in routes[1] if n > 0]

    # Urgências: nós 1, 2 (CRITICAL) e 3, 4 (HIGH)
    van1_crit = [n for n in van1 if n in (1, 2)]
    van2_crit = [n for n in van2 if n in (1, 2)]
    van1_high = [n for n in van1 if n in (3, 4)]
    van2_high = [n for n in van2 if n in (3, 4)]

    # Distribuição equilibrada: exatamente 1 CRITICAL e 1 HIGH para cada van
    assert len(van1_crit) == 1, f"Van 1 deve ter 1 CRITICAL, teve {van1_crit}"
    assert len(van2_crit) == 1, f"Van 2 deve ter 1 CRITICAL, teve {van2_crit}"
    assert len(van1_high) == 1, f"Van 1 deve ter 1 HIGH, teve {van1_high}"
    assert len(van2_high) == 1, f"Van 2 deve ter 1 HIGH, teve {van2_high}"

    # Total de urgências = 2 para cada van
    van1_urgent = van1_crit + van1_high
    van2_urgent = van2_crit + van2_high
    assert len(van1_urgent) == 2
    assert len(van2_urgent) == 2

    # Paradas urgentes devem ser atendidas antes das regulares em cada rota
    for v_idx, van_nodes in enumerate([van1, van2]):
        crit_indices = [i for i, n in enumerate(van_nodes) if n in (1, 2)]
        high_indices = [i for i, n in enumerate(van_nodes) if n in (3, 4)]
        reg_indices = [i for i, n in enumerate(van_nodes) if n in (5, 6, 7, 8)]

        if crit_indices and reg_indices:
            assert max(crit_indices) < min(reg_indices), f"Van {v_idx+1} atendeu regular antes de crítica!"
        if high_indices and reg_indices:
            assert max(high_indices) < min(reg_indices), f"Van {v_idx+1} atendeu regular antes de alta prioridade!"

def test_vrp_three_tier_priorities_and_sectorization():
    """
    Testa os 3 níveis hierárquicos:
    1° Prioridade: Críticos distribuídos equilibrando tempo/distância (makespan) e atendidos imediatamente (perna 1).
    2° Prioridade: Altas priorizadas, mas regulares no caminho podem ser atendidas antes (on-the-way insertion).
    3° Prioridade: Divisão em regiões geográficas evitando cruzamento territorial.
    """
    # 0 = Hub central
    # Setor Norte: 1 (Critico Norte), 2 (Regular no caminho para Alta), 3 (Alta Norte)
    # Setor Sul: 4 (Critico Sul), 5 (Alta Sul), 6 (Regular Sul)
    num_nodes = 7
    durations = [
        [0, 500, 700, 1200, 600, 1300, 1500],   # 0 (Hub)
        [500, 0, 200, 700, 1800, 2200, 2400],   # 1 (Critico Norte)
        [700, 200, 0, 500, 1900, 2300, 2500],   # 2 (Regular Norte - no caminho entre 1 e 3!)
        [1200, 700, 500, 0, 2400, 2700, 2900],  # 3 (Alta Norte)
        [600, 1800, 1900, 2400, 0, 600, 800],   # 4 (Critico Sul)
        [1300, 2200, 2300, 2700, 600, 0, 300],  # 5 (Alta Sul)
        [1500, 2400, 2500, 2900, 800, 300, 0],  # 6 (Regular Sul)
    ]
    distances = [[d * 12 for d in row] for row in durations]

    deliveries = [
        {"id": "1", "name": "Critico Norte", "demand": 10, "priority": "CRITICAL", "critical_medication": True},
        {"id": "2", "name": "Regular Norte (No Caminho)", "demand": 10, "priority": "REGULAR", "critical_medication": False},
        {"id": "3", "name": "Alta Norte", "demand": 10, "priority": "HIGH", "critical_medication": False},
        {"id": "4", "name": "Critico Sul", "demand": 10, "priority": "CRITICAL", "critical_medication": True},
        {"id": "5", "name": "Alta Sul", "demand": 10, "priority": "HIGH", "critical_medication": False},
        {"id": "6", "name": "Regular Sul", "demand": 10, "priority": "REGULAR", "critical_medication": False},
    ]

    solver = VRPSolver(
        durations_matrix_sec=durations,
        distances_matrix_m=distances,
        deliveries_data=deliveries,
        num_vehicles=2,
        capacity_per_vehicle=50,
        population_size=25,
        generations=15
    )
    res = solver.solve()
    routes = res["routes_by_vehicle"]
    assert len(routes) == 2

    van1 = [n for n in routes[0] if n > 0]
    van2 = [n for n in routes[1] if n > 0]

    # Prioridade 1: Ambas as vans devem ter recebido 1 crítico (tempo/makespan balanceado)
    van_with_norte = van1 if 1 in van1 else van2
    van_with_sul = van2 if 1 in van1 else van1

    assert 1 in van_with_norte and 4 in van_with_sul
    # 1ª perna de cada van deve ser o ponto crítico
    assert van_with_norte[0] == 1, "Ponto crítico Norte deve ser atendido imediatamente na 1ª parada"
    assert van_with_sul[0] == 4, "Ponto crítico Sul deve ser atendido imediatamente na 1ª parada"

    # Prioridade 3: Setorização regional (nós 1, 2, 3 no Norte; nós 4, 5, 6 no Sul)
    assert set(van_with_norte) == {1, 2, 3}, f"Van Norte deve conter apenas pontos Norte, teve {van_with_norte}"
    assert set(van_with_sul) == {4, 5, 6}, f"Van Sul deve conter apenas pontos Sul, teve {van_with_sul}"

    # Prioridade 2: No setor Norte, como o Regular 2 está exatamente no caminho entre 1 e 3
    # (1 -> 2 -> 3 custa 200 + 500 = 700s; direto 1 -> 3 custa 700s, logo desvio é zero!)
    assert van_with_norte.index(2) < van_with_norte.index(3), "Regular no caminho deve ser atendido antes da Alta sem desvio excessivo"

def test_vrp_traffic_and_dwell_times():
    # Testa VRP com horário de saída às 08:00 (Pico da manhã em Salvador) vs Madrugada às 03:00 (Livre)
    durations = [
        [0, 600, 900],
        [600, 0, 700],
        [900, 700, 0]
    ]
    distances = [[d * 12 for d in row] for row in durations]
    deliveries = [
        {"id": "d1", "name": "Hospital A", "demand": 10, "priority": "CRITICAL", "service_duration_minutes": 20, "city": "Salvador"},
        {"id": "d2", "name": "Hospital B", "demand": 10, "priority": "REGULAR", "service_duration_minutes": 15, "city": "Salvador"}
    ]

    # Solver 1: Saída no Pico da Manhã (08:00 / 480 min) com 15 min de serviço padrão
    solver_peak = VRPSolver(
        durations_matrix_sec=durations,
        distances_matrix_m=distances,
        deliveries_data=deliveries,
        num_vehicles=1,
        departure_time_minutes=480.0,
        default_service_minutes=15,
        base_city="Salvador",
        points_cities=["Salvador", "Salvador", "Salvador"]
    )
    res_peak = solver_peak.solve()

    # Solver 2: Saída na Madrugada (03:00 / 180 min - Trânsito 1.0)
    solver_offpeak = VRPSolver(
        durations_matrix_sec=durations,
        distances_matrix_m=distances,
        deliveries_data=deliveries,
        num_vehicles=1,
        departure_time_minutes=180.0,
        default_service_minutes=15,
        base_city="Salvador",
        points_cities=["Salvador", "Salvador", "Salvador"]
    )
    res_offpeak = solver_offpeak.solve()

    # O tempo total no pico da manhã deve ser estritamente maior que na madrugada devido ao multiplicador de trânsito
    assert res_peak["total_time_minutes"] > res_offpeak["total_time_minutes"]
    # E o tempo total deve incluir os tempos de serviço (20 + 15 = 35 min)
    assert res_peak["total_time_minutes"] >= 35.0


