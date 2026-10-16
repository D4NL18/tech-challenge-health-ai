"""
Representação Cromossômica de Permutação para Roteamento Médico VRP (P-024).
"""

import random
from typing import List, Dict, Any, Optional

class VRPChromosome:
    def __init__(self, sequence: List[int], fitness: float = float('inf')):
        # sequence é a permutação de índices de entrega [1, 2, ..., N] (onde 0 é o depósito central)
        self.sequence = sequence
        self.fitness = fitness
        self.total_time_minutes: float = 0.0
        self.total_distance_km: float = 0.0
        self.routes_by_vehicle: List[List[int]] = []
        self.penalties: Dict[str, float] = {}

    @classmethod
    def random(cls, num_deliveries: int) -> 'VRPChromosome':
        """
        Gera uma permutação aleatória dos índices 1 a num_deliveries.
        """
        seq = list(range(1, num_deliveries + 1))
        random.shuffle(seq)
        return cls(sequence=seq)

    def copy(self) -> 'VRPChromosome':
        c = VRPChromosome(sequence=list(self.sequence), fitness=self.fitness)
        c.total_time_minutes = self.total_time_minutes
        c.total_distance_km = self.total_distance_km
        c.routes_by_vehicle = [list(r) for r in self.routes_by_vehicle]
        c.penalties = dict(self.penalties)
        return c
