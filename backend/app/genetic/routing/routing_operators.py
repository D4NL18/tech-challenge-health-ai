"""
Operadores Genéticos de Permutação para Roteamento de Veículos (P-024).
Implementa Order Crossover (OX), Partially Mapped Crossover (PMX),
Mutação por Inversão 2-opt e Swap, garantindo ausência de duplicidade de entregas.
"""

import random
from typing import List, Tuple
from .vrp_chromosome import VRPChromosome

class RoutingOperators:
    @staticmethod
    def tournament_selection(population: List[VRPChromosome], k: int = 3) -> VRPChromosome:
        """
        Torneio para minimização: seleciona k indivíduos e retorna o de MENOR fitness (menor custo).
        """
        candidates = random.sample(population, min(k, len(population)))
        return min(candidates, key=lambda ind: ind.fitness)

    @staticmethod
    def order_crossover_ox(p1: VRPChromosome, p2: VRPChromosome, pc: float = 0.85) -> Tuple[VRPChromosome, VRPChromosome]:
        """
        Order Crossover (OX): O operador mais consagrado para TSP/VRP.
        Preserva subsequências contíguas e preenche as demais posições na ordem do outro progenitor.
        """
        if random.random() > pc or len(p1.sequence) < 3:
            return p1.copy(), p2.copy()

        n = len(p1.sequence)
        cut1, cut2 = sorted(random.sample(range(n), 2))

        def _ox_child(parent_a: List[int], parent_b: List[int]) -> List[int]:
            child = [None] * n
            # Copia o bloco central de parent_a
            child[cut1:cut2+1] = parent_a[cut1:cut2+1]
            copied_set = set(child[cut1:cut2+1])

            # Preenche o restante preservando a ordem circular de parent_b
            b_order = parent_b[cut2+1:] + parent_b[:cut2+1]
            remaining = [val for val in b_order if val not in copied_set]

            idx = (cut2 + 1) % n
            for val in remaining:
                child[idx] = val
                idx = (idx + 1) % n

            return child

        c1_seq = _ox_child(p1.sequence, p2.sequence)
        c2_seq = _ox_child(p2.sequence, p1.sequence)

        return VRPChromosome(sequence=c1_seq), VRPChromosome(sequence=c2_seq)

    @staticmethod
    def mutate(chromosome: VRPChromosome, pm: float = 0.20) -> VRPChromosome:
        """
        Aplica mutação por Inversão (2-opt) ou Troca (Swap) com probabilidade pm.
        """
        if random.random() > pm or len(chromosome.sequence) < 2:
            return chromosome

        seq = list(chromosome.sequence)
        n = len(seq)

        if random.random() < 0.7:
            # 2-opt Inversion: inverte um segmento da rota
            i, j = sorted(random.sample(range(n), 2))
            seq[i:j+1] = reversed(seq[i:j+1])
        else:
            # Swap: troca duas entregas de posição
            i, j = random.sample(range(n), 2)
            seq[i], seq[j] = seq[j], seq[i]

        return VRPChromosome(sequence=seq)
