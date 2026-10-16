"""
Motor Evolutivo de Otimização Genética (P-010, P-012, P-013).
Executa o ciclo geracional com elitismo, rastreamento de convergência e persistência de histórico.
"""

import time
import numpy as np
from typing import Dict, Any, List, Optional, Callable
from .chromosome import HyperparameterGeneSpace, Chromosome
from .operators import GeneticOperators
from .fitness import ClinicalFitnessEvaluator
from .visualizer import LiveGeneticVisualizer

class GeneticHyperparameterOptimizer:
    def __init__(
        self,
        X: np.ndarray,
        y: np.ndarray,
        model_name: str,
        dataset_name: str = "cancer",
        population_size: int = 40,
        generations: int = 20,
        mutation_rate: float = 0.15,
        crossover_rate: float = 0.85,
        elitism_count: int = 2,
        k_tournament: int = 3,
        verbose: bool = True,
        live_plot: bool = False,
        plot_save_path: Optional[str] = None,
        on_generation: Optional[Callable[[Dict[str, Any], int], None]] = None
    ):
        self.X = X
        self.y = y
        self.model_name = model_name
        self.dataset_name = dataset_name
        self.population_size = population_size
        self.generations = generations
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        self.elitism_count = elitism_count
        self.k_tournament = k_tournament
        self.verbose = verbose
        self.live_plot = live_plot
        self.plot_save_path = plot_save_path
        self.on_generation = on_generation

        self.space = HyperparameterGeneSpace.get_space(model_name)
        self.evaluator = ClinicalFitnessEvaluator(X, y, model_name)
        
        self.visualizer: Optional[LiveGeneticVisualizer] = None
        if self.live_plot or self.plot_save_path:
            self.visualizer = LiveGeneticVisualizer(
                model_name=self.model_name,
                dataset_name=self.dataset_name,
                total_generations=self.generations,
                interactive=self.live_plot
            )

        # Históricos de convergência (Slide 454: Convergência e Diversidade Genética)
        self.history = {
            "generation": [],
            "best_fitness": [],
            "mean_fitness": [],
            "std_fitness": [],
            "diversity_ratio": [],
            "best_metrics": []
        }
        self.best_chromosome: Optional[Chromosome] = None

    def run(self) -> Dict[str, Any]:
        """
        Executa o loop geracional completo do Algoritmo Genético.
        """
        start_time = time.time()
        if self.verbose:
            print(f"=== Iniciando GA Hyperopt: {self.model_name} (Pop={self.population_size}, Gen={self.generations}) ===")

        # 1. População Inicial
        population = [Chromosome.random(self.space) for _ in range(self.population_size)]

        # Avaliação da geração 0
        for ind in population:
            self.evaluator.evaluate(ind)

        population.sort(key=lambda ind: ind.fitness, reverse=True)
        self.best_chromosome = population[0].copy()

        # 2. Ciclo Geracional
        for gen in range(1, self.generations + 1):
            fits = [ind.fitness for ind in population]
            best_fit = float(np.max(fits))
            mean_fit = float(np.mean(fits))
            std_fit = float(np.std(fits))

            # Métricas de diversidade (Slide 454: proporção de soluções únicas)
            unique_chromosomes = len(set(tuple(sorted(ind.genes.items())) for ind in population))
            diversity = round(unique_chromosomes / len(population), 4)

            if population[0].fitness > self.best_chromosome.fitness:
                self.best_chromosome = population[0].copy()

            self.history["generation"].append(gen)
            self.history["best_fitness"].append(round(best_fit, 4))
            self.history["mean_fitness"].append(round(mean_fit, 4))
            self.history["std_fitness"].append(round(std_fit, 4))
            self.history["diversity_ratio"].append(diversity)
            self.history["best_metrics"].append(self.best_chromosome.metrics)

            if self.verbose:
                print(f"[Gen {gen:02d}/{self.generations:02d}] Best F2={best_fit:.4f} | Mean F2={mean_fit:.4f} | Std={std_fit:.4f} | Div={diversity:.2f} | Recall={self.best_chromosome.metrics.get('recall', 0):.4f}")

            # Atualiza visualização gráfica dinâmica
            if self.visualizer:
                self.visualizer.update(self.history, gen)
            if self.on_generation:
                try:
                    self.on_generation(self.history, gen)
                except Exception:
                    pass

            # Critério de Parada precoce se todas as gerações foram executadas
            if gen == self.generations:
                break

            # 3. Formação da Nova Geração com Elitismo (P-012)
            new_population: List[Chromosome] = []
            
            # Elitismo: preserva os melhores intactos
            for i in range(min(self.elitism_count, len(population))):
                new_population.append(population[i].copy())

            # Reprodução (Seleção, Crossover e Mutação)
            while len(new_population) < self.population_size:
                p1 = GeneticOperators.tournament_selection(population, k=self.k_tournament)
                p2 = GeneticOperators.tournament_selection(population, k=self.k_tournament)

                c1, c2 = GeneticOperators.crossover(p1, p2, self.space, pc=self.crossover_rate)
                c1 = GeneticOperators.mutate(c1, self.space, pm=self.mutation_rate)
                c2 = GeneticOperators.mutate(c2, self.space, pm=self.mutation_rate)

                self.evaluator.evaluate(c1)
                new_population.append(c1)

                if len(new_population) < self.population_size:
                    self.evaluator.evaluate(c2)
                    new_population.append(c2)

            population = sorted(new_population, key=lambda ind: ind.fitness, reverse=True)

        elapsed = round(time.time() - start_time, 2)
        if self.verbose:
            print(f"=== Otimização concluída em {elapsed}s. Melhor F2: {self.best_chromosome.fitness:.4f} ===")

        # Salva o gráfico gerado
        if self.visualizer:
            save_path = self.plot_save_path or f"weights/plots/genetic_convergence_{self.model_name}_{self.dataset_name}.png"
            self.visualizer.save(save_path)
            self.visualizer.close()

        return {
            "model_name": self.model_name,
            "elapsed_seconds": elapsed,
            "best_hyperparameters": self.best_chromosome.genes,
            "best_metrics": self.best_chromosome.metrics,
            "convergence_history": self.history
        }
