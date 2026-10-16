"""
Solucionador Evolutivo de Roteamento de Veículos (VRP Solver - P-020 a P-024).
Orquestra o Algoritmo Genético sobre a matriz de tempos OSRM e devolve a solução ótima,
minimizando o makespan das urgências e balanceando as rotas entre múltiplos motoristas.
"""

import time
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from .vrp_chromosome import VRPChromosome
from .routing_operators import RoutingOperators
from .routing_fitness import VRPFitnessEvaluator

class VRPSolver:
    def __init__(
        self,
        durations_matrix_sec: List[List[float]],
        distances_matrix_m: List[List[float]],
        deliveries_data: List[Dict[str, Any]],
        num_vehicles: int = 2,
        capacity_per_vehicle: float = 100.0,
        max_distance_km_per_vehicle: float = 150.0,
        population_size: int = 50,
        generations: int = 30,
        mutation_rate: float = 0.20,
        crossover_rate: float = 0.85,
        elitism_count: int = 2
    ):
        self.num_deliveries = len(deliveries_data)
        self.evaluator = VRPFitnessEvaluator(
            durations_matrix_sec=durations_matrix_sec,
            distances_matrix_m=distances_matrix_m,
            deliveries_data=deliveries_data,
            num_vehicles=num_vehicles,
            capacity_per_vehicle=capacity_per_vehicle,
            max_distance_km_per_vehicle=max_distance_km_per_vehicle
        )
        self.population_size = max(10, population_size)
        self.generations = max(5, generations)
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        self.elitism_count = elitism_count

        self.history: List[float] = []
        self.generation_metrics: List[Dict[str, float]] = []
        self.best_chromosome: Optional[VRPChromosome] = None

    def _generate_nearest_neighbor_individual(self) -> VRPChromosome:
        """
        Hotstart Heurístico com Priorização Médica Estruturada:
        Constrói uma solução inicial de alta qualidade ordenando por vizinho mais próximo
        dentro de cada nível de prioridade (Crítica -> Alta -> Regular).
        """
        if self.num_deliveries <= 1:
            return VRPChromosome(sequence=list(range(1, self.num_deliveries + 1)))

        crit_nodes: List[int] = []
        high_nodes: List[int] = []
        reg_nodes: List[int] = []

        for i, d in enumerate(self.evaluator.deliveries):
            prio = str(d.get("priority", "REGULAR")).upper()
            is_crit = d.get("critical_medication", False) or prio in ("CRITICAL", "IMMEDIATE", "URGENT")
            if is_crit:
                crit_nodes.append(i + 1)
            elif prio == "HIGH":
                high_nodes.append(i + 1)
            else:
                reg_nodes.append(i + 1)

        def tour_nearest_neighbor(nodes: List[int], start_loc: int) -> Tuple[List[int], int]:
            if not nodes:
                return [], start_loc
            unvisited = set(nodes)
            curr = start_loc
            tour: List[int] = []
            while unvisited:
                nxt = min(unvisited, key=lambda d_idx: self.evaluator.durations[curr][d_idx])
                tour.append(nxt)
                unvisited.remove(nxt)
                curr = nxt
            return tour, curr

        tour_crit, last_loc = tour_nearest_neighbor(crit_nodes, 0)
        tour_high, last_loc = tour_nearest_neighbor(high_nodes, last_loc)
        tour_reg, _ = tour_nearest_neighbor(reg_nodes, last_loc)

        return VRPChromosome(sequence=tour_crit + tour_high + tour_reg)

    def solve(self) -> Dict[str, Any]:
        start_time = time.time()
        
        # 1. População Inicial
        population: List[VRPChromosome] = []
        
        hotstart_ind = self._generate_nearest_neighbor_individual()
        self.evaluator.evaluate(hotstart_ind)
        population.append(hotstart_ind)

        while len(population) < self.population_size:
            ind = VRPChromosome.random(self.num_deliveries)
            self.evaluator.evaluate(ind)
            population.append(ind)

        population.sort(key=lambda ind: ind.fitness)
        self.best_chromosome = population[0].copy()
        
        # 2. Ciclo Evolutivo
        for gen in range(1, self.generations + 1):
            fits = [ind.fitness for ind in population]
            b_fit = float(np.min(fits))
            m_fit = float(np.mean(fits))
            s_fit = float(np.std(fits))

            # Métricas de Desempenho (Slides 454-455: Convergência e Diversidade)
            unique_solutions = len(set(tuple(ind.sequence) for ind in population))
            diversity_ratio = round(unique_solutions / len(population), 4)

            if population[0].fitness < self.best_chromosome.fitness:
                self.best_chromosome = population[0].copy()

            self.history.append(round(self.best_chromosome.fitness, 4))
            self.generation_metrics.append({
                "generation": gen,
                "best_fitness": round(self.best_chromosome.fitness, 4),
                "mean_fitness": round(m_fit, 4),
                "std_fitness": round(s_fit, 4),
                "diversity_ratio": diversity_ratio
            })

            if gen == self.generations:
                break

            # Elitismo: preserva os E melhores indivíduos intactos
            new_population: List[VRPChromosome] = []
            for i in range(min(self.elitism_count, len(population))):
                new_population.append(population[i].copy())

            # Reprodução: Seleção por Torneio, Crossover OX e Mutação
            while len(new_population) < self.population_size:
                p1 = RoutingOperators.tournament_selection(population, k=3)
                p2 = RoutingOperators.tournament_selection(population, k=3)

                c1, c2 = RoutingOperators.order_crossover_ox(p1, p2, pc=self.crossover_rate)
                c1 = RoutingOperators.mutate(c1, pm=self.mutation_rate)
                c2 = RoutingOperators.mutate(c2, pm=self.mutation_rate)

                self.evaluator.evaluate(c1)
                new_population.append(c1)

                if len(new_population) < self.population_size:
                    self.evaluator.evaluate(c2)
                    new_population.append(c2)

            population = sorted(new_population, key=lambda ind: ind.fitness)

        # Garante a avaliação consolidada no melhor cromossomo final
        self.evaluator.evaluate(self.best_chromosome)

        elapsed = round(time.time() - start_time, 3)

        return {
            "elapsed_seconds": elapsed,
            "best_fitness": self.best_chromosome.fitness,
            "total_time_minutes": self.best_chromosome.total_time_minutes,
            "total_distance_km": self.best_chromosome.total_distance_km,
            "routes_by_vehicle": self.best_chromosome.routes_by_vehicle,
            "penalties": self.best_chromosome.penalties,
            "fitness_history": self.history,
            "generation_metrics": self.generation_metrics
        }
