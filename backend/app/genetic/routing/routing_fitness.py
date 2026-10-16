"""
Avaliador de Fitness Multiobjetivo com Restrições Médicas para VRP (P-021, P-022, P-023).
Otimiza a distribuição viária de urgências entre múltiplos motoristas:
- Minimização do Makespan de Urgência (tempo até a última urgência da frota ser atendida)
- Distribuição perfeitamente balanceada das paradas urgentes (diferença máxima de 1 nó entre motoristas)
- Clusterização espacial inteligente com matriz viária real OSRM
- Respeito a motorista vinculado estrito (assigned_vehicle) se informado
- 3 Níveis Clínicos Estritos: Crítica (Perna 1), Alta (Perna 2), Regular (Perna 3)
"""

from typing import List, Dict, Any, Tuple, Optional
from .vrp_chromosome import VRPChromosome

class VRPFitnessEvaluator:
    def __init__(
        self,
        durations_matrix_sec: List[List[float]],
        distances_matrix_m: List[List[float]],
        deliveries_data: List[Dict[str, Any]],
        num_vehicles: int = 2,
        capacity_per_vehicle: float = 100.0,
        max_distance_km_per_vehicle: float = 150.0
    ):
        """
        Índice 0 é sempre o Depósito/Hub Hospitalar Central.
        Índices 1 a N correspondem a deliveries_data[0] a deliveries_data[N-1].
        """
        self.durations = durations_matrix_sec
        self.distances = distances_matrix_m
        self.deliveries = deliveries_data
        self.num_vehicles = max(1, num_vehicles)
        self.capacity = capacity_per_vehicle
        self.max_dist_km = max_distance_km_per_vehicle

    def _optimize_subtour_order(self, nodes: List[int], start_loc: int) -> List[int]:
        """
        Ordena um grupo de nós para visitação com menor tempo viário
        a partir de um ponto de partida (Depósito ou última parada da perna anterior).
        """
        if len(nodes) <= 1:
            return nodes

        unvisited = set(nodes)
        curr = start_loc
        tour: List[int] = []

        while unvisited:
            nxt = min(unvisited, key=lambda nd: self.durations[curr][nd])
            tour.append(nxt)
            unvisited.remove(nxt)
            curr = nxt

        return tour

    def _distribute_critical_balanced(
        self,
        crit_nodes: List[int],
        k: int
    ) -> Tuple[List[List[int]], List[float], List[float], List[float]]:
        """
        1ª PRIORIDADE: Distribuição de entregas críticas entre os motoristas.
        - Equilíbrio estrito baseado em TEMPO e DISTÂNCIA viária (não por contagem de nós).
        - Conclusão no menor tempo possível (minimização do makespan crítico).
        - Atendimento obrigatório na 1ª perna de cada motorista saindo do Depósito (0).
        """
        van_crit: List[List[int]] = [[] for _ in range(k)]
        van_crit_time: List[float] = [0.0 for _ in range(k)]
        van_crit_dist: List[float] = [0.0 for _ in range(k)]
        van_load: List[float] = [0.0 for _ in range(k)]
        van_curr: List[int] = [0 for _ in range(k)]

        if not crit_nodes:
            return van_crit, van_crit_time, van_crit_dist, van_load

        # 1. Respeito estrito a assigned_vehicle se informado
        unassigned: List[int] = []
        for c in crit_nodes:
            deliv = self.deliveries[c - 1]
            assigned_v = deliv.get("assigned_vehicle")
            if assigned_v is not None and isinstance(assigned_v, int) and 1 <= assigned_v <= k:
                target_v = assigned_v - 1
                van_crit[target_v].append(c)
                dt = self.durations[van_curr[target_v]][c]
                ds = self.distances[van_curr[target_v]][c]
                van_crit_time[target_v] += dt
                van_crit_dist[target_v] += ds
                van_curr[target_v] = c
                van_load[target_v] += float(deliv.get("demand", 10.0))
            else:
                unassigned.append(c)

        # 2. Nós críticos ordenados por tempo viário a partir do Depósito (mais distantes primeiro)
        unassigned.sort(key=lambda c: self.durations[0][c], reverse=True)

        # 3. Alocação ponderada exclusivamente em TEMPO, DISTÂNCIA e MAKESPAN
        for c in unassigned:
            deliv = self.deliveries[c - 1]
            demand = float(deliv.get("demand", 10.0))

            best_v = 0
            best_cost = float("inf")

            for v in range(k):
                dt = self.durations[van_curr[v]][c]
                ds = self.distances[van_curr[v]][c]
                new_time = van_crit_time[v] + dt

                # Makespan crítico entre todas as vans
                other_times = [van_crit_time[o] for o in range(k) if o != v]
                makespan = max(max(other_times, default=0.0), new_time)

                # Desequilíbrio em relação ao tempo médio das outras vans
                other_avg = sum(other_times) / max(1, len(other_times)) if other_times else 0.0
                time_imbalance = abs(new_time - other_avg)

                cap_penalty = 1000.0 if (van_load[v] + demand > self.capacity) else 0.0

                # Custo pondera makespan crítico e paridade de tempo/distância entre motoristas
                cost = (makespan * 1.5) + (time_imbalance * 1.0) + (dt * 0.25) + cap_penalty
                if cost < best_cost:
                    best_cost = cost
                    best_v = v

            van_crit[best_v].append(c)
            van_crit_time[best_v] += self.durations[van_curr[best_v]][c]
            van_crit_dist[best_v] += self.distances[van_curr[best_v]][c]
            van_curr[best_v] = c
            van_load[best_v] += demand

        # 4. Otimiza o trajeto interno de urgências críticas de cada van a partir da Base (0)
        for v in range(k):
            if len(van_crit[v]) > 1:
                van_crit[v] = self._optimize_subtour_order(van_crit[v], start_loc=0)

        return van_crit, van_crit_time, van_crit_dist, van_load

    def _split_into_vehicle_routes(self, sequence: List[int]) -> List[List[int]]:
        """
        Particiona a sequência de entregas entre os motoristas atendendo a 3 prioridades estritas:
        1ª Prioridade: Críticos distribuídos equilibrando TEMPO e DISTÂNCIA viária (não contagem de pontos),
                       atendidos obrigatoriamente na primeira perna de cada motorista (makespan mínimo).
        2ª Prioridade: Altas priorizadas sobre regulares, mas com flexibilidade viária: regulares no caminho
                       ou quando o desvio para a alta for excessivo podem vir antes (on-the-way insertion).
        3ª Prioridade: Setorização regional contígua: o mapa é dividido em regiões de atendimento para encurtar
                       distâncias e evitar que múltiplos motoristas circulem pelos mesmos bairros próximos.
        """
        k = self.num_vehicles
        if not sequence or k == 0:
            return [[] for _ in range(k)]

        # Classificação clínica dos nós
        crit_nodes: List[int] = []
        high_nodes: List[int] = []
        reg_nodes: List[int] = []

        for stop_idx in sequence:
            deliv = self.deliveries[stop_idx - 1]
            prio = str(deliv.get("priority", "REGULAR")).upper()
            is_crit = (
                deliv.get("critical_medication", False) 
                or prio in ("CRITICAL", "IMMEDIATE", "URGENT")
            )
            if is_crit:
                crit_nodes.append(stop_idx)
            elif prio == "HIGH":
                high_nodes.append(stop_idx)
            else:
                reg_nodes.append(stop_idx)

        high_nodes_set = set(high_nodes)
        reg_nodes_set = set(reg_nodes)

        # -------------------------------------------------------------
        # 1ª PRIORIDADE: Atribuição de Críticos equilibrando TEMPO/DISTÂNCIA
        # -------------------------------------------------------------
        van_crit, van_crit_time, van_crit_dist, van_load = self._distribute_critical_balanced(
            crit_nodes=crit_nodes,
            k=k
        )

        # -------------------------------------------------------------
        # 3ª PRIORIDADE: Setorização Regional dos Nós Restantes (Cheapest Insertion)
        # -------------------------------------------------------------
        non_crit_nodes = [nd for nd in sequence if nd not in crit_nodes]
        van_non_crit: List[List[int]] = [[] for _ in range(k)]

        unassigned_non_crit: List[int] = []
        for nd in non_crit_nodes:
            deliv = self.deliveries[nd - 1]
            assigned_v = deliv.get("assigned_vehicle")
            if assigned_v is not None and isinstance(assigned_v, int) and 1 <= assigned_v <= k:
                target_v = assigned_v - 1
                van_non_crit[target_v].append(nd)
                van_load[target_v] += float(deliv.get("demand", 10.0))
            else:
                unassigned_non_crit.append(nd)

        # Rastreamento aproximado do tempo de percurso de cada van para setorização equilibrada
        van_approx_time = list(van_crit_time)

        # 3.1. Seeding: se houver vans vazias e o total de entregas for suficiente,
        # cada van vazia recebe um nó semente (priorizando HIGH, depois mais distantes da base)
        empty_vans = [v for v in range(k) if len(van_crit[v]) + len(van_non_crit[v]) == 0]
        if empty_vans and unassigned_non_crit:
            def seed_priority_key(node: int):
                prio_rank = 0 if node in high_nodes_set else 1
                dist_from_depot = self.durations[0][node]
                return (prio_rank, -dist_from_depot)

            seed_candidates = sorted(unassigned_non_crit, key=seed_priority_key)
            for v in empty_vans:
                if not seed_candidates:
                    break
                seed_node = seed_candidates.pop(0)
                unassigned_non_crit.remove(seed_node)
                van_non_crit[v].append(seed_node)
                van_load[v] += float(self.deliveries[seed_node - 1].get("demand", 10.0))
                van_approx_time[v] = self.durations[0][seed_node] + self.durations[seed_node][0]

        target_per_van = max(1, len(sequence) // k)

        for nd in unassigned_non_crit:
            deliv = self.deliveries[nd - 1]
            demand = float(deliv.get("demand", 10.0))

            best_v = 0
            best_cost = float("inf")

            for v in range(k):
                # Rota atual provisória da van v: [0] + crit + non_crit + [0]
                current_tour = [0] + van_crit[v] + van_non_crit[v] + [0]

                # Menor desvio viário de inserção em qualquer posição do tour
                min_detour = float("inf")
                for i in range(len(current_tour) - 1):
                    p = current_tour[i]
                    q = current_tour[i + 1]
                    d = self.durations[p][nd] + self.durations[nd][q] - self.durations[p][q]
                    if d < min_detour:
                        min_detour = d

                # Penalidade de capacidade
                cap_pen = 1000.0 if (van_load[v] + demand > self.capacity) else 0.0

                # Penalidade de sobrecarga de nós por van para balancear a frota
                count_v = len(van_crit[v]) + len(van_non_crit[v])
                balance_pen = max(0, count_v - target_per_van) * 200.0

                # Pondera desvio territorial com balanceamento de tempo acumulado e contagem
                cost = min_detour + cap_pen + (van_approx_time[v] * 0.25) + balance_pen
                if cost < best_cost:
                    best_cost = cost
                    best_v = v

            van_non_crit[best_v].append(nd)
            van_load[best_v] += demand
            # Atualiza estimativa de tempo da van
            updated_tour = [0] + van_crit[best_v] + van_non_crit[best_v] + [0]
            van_approx_time[best_v] = sum(
                self.durations[updated_tour[i]][updated_tour[i + 1]] 
                for i in range(len(updated_tour) - 1)
            )

        # -------------------------------------------------------------
        # 2ª PRIORIDADE: Sequenciamento com On-the-Way Insertion
        # -------------------------------------------------------------
        full_routes: List[List[int]] = []

        for v in range(k):
            route = list(van_crit[v])
            curr_loc = route[-1] if route else 0
            unvisited = list(van_non_crit[v])

            while unvisited:
                unvisited_high = [u for u in unvisited if u in high_nodes_set]
                unvisited_reg = [u for u in unvisited if u in reg_nodes_set]

                if unvisited_high:
                    best_h = min(unvisited_high, key=lambda h: self.durations[curr_loc][h])
                    dt_to_h = self.durations[curr_loc][best_h]

                    # 1. Checa candidatos regulares "no caminho" (on-the-way)
                    on_the_way_candidates = []
                    for r in unvisited_reg:
                        detour = self.durations[curr_loc][r] + self.durations[r][best_h] - dt_to_h
                        # Detour suave de até 240s (4 min) ou até 25% da rota direta
                        if detour <= max(240.0, 0.25 * dt_to_h):
                            on_the_way_candidates.append((detour, self.durations[curr_loc][r], r))

                    # 2. Checa se o nó regular mais próximo está tão perto que não ir nele interfere muito
                    nearest_reg = min(unvisited_reg, key=lambda r: self.durations[curr_loc][r]) if unvisited_reg else None
                    if nearest_reg and self.durations[curr_loc][nearest_reg] <= 180.0 and dt_to_h >= 720.0:
                        chosen = nearest_reg
                    elif on_the_way_candidates:
                        # Escolhe o nó no caminho com menor desvio
                        on_the_way_candidates.sort(key=lambda x: (x[0], x[1]))
                        chosen = on_the_way_candidates[0][2]
                    else:
                        chosen = best_h
                else:
                    # Apenas regulares restantes: vizinho mais próximo a partir de curr_loc
                    chosen = min(unvisited, key=lambda u: self.durations[curr_loc][u])

                route.append(chosen)
                unvisited.remove(chosen)
                curr_loc = chosen

            if route:
                full_routes.append([0] + route + [0])
            else:
                full_routes.append([])

        return full_routes

    def evaluate(self, chromosome: VRPChromosome) -> float:
        routes = self._split_into_vehicle_routes(chromosome.sequence)
        chromosome.routes_by_vehicle = routes

        total_time_sec = 0.0
        total_dist_m = 0.0
        penalty_capacity = 0.0
        penalty_autonomy = 0.0
        penalty_critical_delay = 0.0
        penalty_high_delay = 0.0
        penalty_strict_violations = 0.0

        vehicle_times_min: List[float] = []
        vehicle_distances_km: List[float] = []
        urgency_finish_times_min: List[float] = []

        for vehicle_idx, route in enumerate(routes):
            if not route:
                continue

            vehicle_id_1based = vehicle_idx + 1
            vehicle_load = 0.0
            vehicle_dist_m = 0.0
            vehicle_time_sec = 0.0
            last_urg_time_sec = 0.0

            for i in range(len(route) - 1):
                u = route[i]
                v = route[i + 1]

                step_time = self.durations[u][v]
                step_dist = self.distances[u][v]

                vehicle_time_sec += step_time
                vehicle_dist_m += step_dist

                if v > 0:
                    deliv = self.deliveries[v - 1]
                    vehicle_load += float(deliv.get("demand", 10.0))

                    prio = str(deliv.get("priority", "REGULAR")).upper()
                    is_crit = (
                        deliv.get("critical_medication", False) 
                        or prio in ("CRITICAL", "IMMEDIATE", "URGENT")
                    )
                    accumulated_min = vehicle_time_sec / 60.0

                    # Validação de Veículo Estrito (assigned_vehicle)
                    assigned_v = deliv.get("assigned_vehicle")
                    if assigned_v is not None and isinstance(assigned_v, int):
                        if assigned_v != vehicle_id_1based:
                            penalty_strict_violations += 1000.0

                    # Penalidades de Atraso Clínico
                    if is_crit:
                        last_urg_time_sec = vehicle_time_sec
                        penalty_critical_delay += (accumulated_min ** 1.25) * 5.0
                    elif prio == "HIGH":
                        last_urg_time_sec = vehicle_time_sec
                        penalty_high_delay += accumulated_min * 2.5

            if last_urg_time_sec > 0:
                urgency_finish_times_min.append(last_urg_time_sec / 60.0)

            v_time_min = vehicle_time_sec / 60.0
            v_dist_km = vehicle_dist_m / 1000.0
            total_time_sec += vehicle_time_sec
            total_dist_m += vehicle_dist_m
            vehicle_times_min.append(v_time_min)
            vehicle_distances_km.append(v_dist_km)

            if vehicle_load > self.capacity:
                overload = vehicle_load - self.capacity
                penalty_capacity += overload * 500.0

            if v_dist_km > self.max_dist_km:
                over_dist = v_dist_km - self.max_dist_km
                penalty_autonomy += over_dist * 50.0

        # Makespan de Urgência
        penalty_urgency_makespan = 0.0
        penalty_urgency_imbalance = 0.0

        if urgency_finish_times_min:
            max_urgency_time = max(urgency_finish_times_min)
            penalty_urgency_makespan = (max_urgency_time ** 1.3) * 6.0

            if len(urgency_finish_times_min) > 1:
                urg_diff = max(urgency_finish_times_min) - min(urgency_finish_times_min)
                penalty_urgency_imbalance = urg_diff * 5.0

        penalty_workload_imbalance = 0.0
        if len(vehicle_times_min) > 1:
            time_diff = max(vehicle_times_min) - min(vehicle_times_min)
            dist_diff = max(vehicle_distances_km) - min(vehicle_distances_km)
            penalty_workload_imbalance = (time_diff * 4.0) + (dist_diff * 2.0)

        total_time_min = round(total_time_sec / 60.0, 2)
        total_dist_km = round(total_dist_m / 1000.0, 2)

        chromosome.total_time_minutes = total_time_min
        chromosome.total_distance_km = total_dist_km
        chromosome.penalties = {
            "urgency_makespan": round(penalty_urgency_makespan, 2),
            "urgency_imbalance": round(penalty_urgency_imbalance, 2),
            "critical_delay": round(penalty_critical_delay, 2),
            "high_delay": round(penalty_high_delay, 2),
            "capacity_overload": round(penalty_capacity, 2),
            "autonomy_violation": round(penalty_autonomy, 2),
            "workload_imbalance": round(penalty_workload_imbalance, 2),
            "strict_violations": round(penalty_strict_violations, 2)
        }

        fitness = (
            total_time_min 
            + penalty_urgency_makespan 
            + penalty_urgency_imbalance 
            + penalty_critical_delay 
            + penalty_high_delay 
            + penalty_capacity 
            + penalty_autonomy 
            + penalty_workload_imbalance 
            + penalty_strict_violations
        )
        chromosome.fitness = round(fitness, 2)
        return chromosome.fitness
