"""
Operadores Genéticos Especializados para Hiperparâmetros (P-010).
Implementa Seleção por Torneio e Roleta, Crossover Uniforme/Aritmético e Mutação Gaussiana com bounds.
"""

import random
import numpy as np
from typing import List, Tuple, Dict, Any
from .chromosome import Chromosome

class GeneticOperators:
    @staticmethod
    def tournament_selection(population: List[Chromosome], k: int = 3) -> Chromosome:
        """
        Seleção por Torneio Estocástico: seleciona k indivíduos aleatórios e escolhe o de maior fitness.
        """
        candidates = random.sample(population, min(k, len(population)))
        return max(candidates, key=lambda ind: ind.fitness)

    @staticmethod
    def roulette_selection(population: List[Chromosome]) -> Chromosome:
        """
        Seleção por Roleta proporcional ao fitness (com deslocamento para fitness não-negativo).
        """
        min_fit = min(ind.fitness for ind in population)
        adjusted_fits = [ind.fitness - min_fit + 1e-4 for ind in population]
        total_fit = sum(adjusted_fits)
        r = random.uniform(0, total_fit)
        cum = 0.0
        for ind, fit in zip(population, adjusted_fits):
            cum += fit
            if cum >= r:
                return ind
        return population[-1]

    @staticmethod
    def crossover(parent1: Chromosome, parent2: Chromosome, space: Dict[str, Dict[str, Any]], pc: float = 0.85) -> Tuple[Chromosome, Chromosome]:
        """
        Cruzamento Uniforme e Aritmético:
        Com probabilidade pc, recombina os genes de parent1 e parent2.
        """
        if random.random() > pc:
            return parent1.copy(), parent2.copy()

        child1_genes = {}
        child2_genes = {}

        for gene_name, spec in space.items():
            val1 = parent1.genes.get(gene_name)
            val2 = parent2.genes.get(gene_name)
            gtype = spec["type"]

            if gtype in ["float", "float_log"] and val1 is not None and val2 is not None:
                # Crossover aritmético para números reais contínuos
                alpha = random.random()
                c1 = alpha * val1 + (1 - alpha) * val2
                c2 = (1 - alpha) * val1 + alpha * val2
                b_min, b_max = spec["bounds"]
                child1_genes[gene_name] = round(max(b_min, min(b_max, c1)), 4)
                child2_genes[gene_name] = round(max(b_min, min(b_max, c2)), 4)
            else:
                # Crossover uniforme para inteiros e categóricos
                if random.random() < 0.5:
                    child1_genes[gene_name] = val1
                    child2_genes[gene_name] = val2
                else:
                    child1_genes[gene_name] = val2
                    child2_genes[gene_name] = val1

        return Chromosome(child1_genes), Chromosome(child2_genes)

    @staticmethod
    def mutate(chromosome: Chromosome, space: Dict[str, Dict[str, Any]], pm: float = 0.15) -> Chromosome:
        """
        Mutação Bounded: adiciona ruído gaussiano a números ou troca categoria, respeitando os limites.
        """
        mutated_genes = dict(chromosome.genes)

        for gene_name, spec in space.items():
            if random.random() < pm:
                gtype = spec["type"]
                b_min, b_max = spec.get("bounds", (None, None))

                if gtype == "int":
                    current = mutated_genes.get(gene_name, b_min)
                    delta = int(np.random.normal(0, max(1, (b_max - b_min) * 0.1)))
                    mutated_genes[gene_name] = int(max(b_min, min(b_max, current + delta)))
                elif gtype == "int_or_none":
                    if random.random() < 0.2:
                        mutated_genes[gene_name] = None
                    else:
                        current = mutated_genes.get(gene_name) or b_min
                        delta = int(np.random.normal(0, max(1, (b_max - b_min) * 0.1)))
                        mutated_genes[gene_name] = int(max(b_min, min(b_max, current + delta)))
                elif gtype == "float":
                    current = mutated_genes.get(gene_name, (b_min + b_max) / 2)
                    delta = float(np.random.normal(0, (b_max - b_min) * 0.1))
                    mutated_genes[gene_name] = round(float(max(b_min, min(b_max, current + delta))), 4)
                elif gtype == "float_log":
                    # Mutação no espaço logarítmico
                    current = mutated_genes.get(gene_name, b_min)
                    log_val = np.log10(max(1e-6, current))
                    delta_log = float(np.random.normal(0, 0.3))
                    new_val = 10 ** (log_val + delta_log)
                    mutated_genes[gene_name] = round(float(max(b_min, min(b_max, new_val))), 5)
                elif gtype == "cat":
                    choices = spec["choices"]
                    mutated_genes[gene_name] = random.choice(choices)

        return Chromosome(mutated_genes)
