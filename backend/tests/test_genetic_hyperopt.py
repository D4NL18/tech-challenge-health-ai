import pytest
import numpy as np
from app.genetic.hyperopt.chromosome import HyperparameterGeneSpace, Chromosome
from app.genetic.hyperopt.operators import GeneticOperators
from app.genetic.hyperopt.fitness import ClinicalFitnessEvaluator
from app.genetic.hyperopt.optimizer import GeneticHyperparameterOptimizer

def test_chromosome_bounds_and_sklearn_params():
    space = HyperparameterGeneSpace.get_space("random_forest")
    chrom = Chromosome.random(space)
    
    assert "n_estimators" in chrom.genes
    assert 20 <= chrom.genes["n_estimators"] <= 250
    assert chrom.genes["criterion"] in ["gini", "entropy", "log_loss"]
    
    params = chrom.to_sklearn_params("random_forest")
    assert isinstance(params, dict)
    assert "n_estimators" in params

def test_genetic_operators_mutation_and_crossover():
    space = HyperparameterGeneSpace.get_space("random_forest")
    p1 = Chromosome.random(space)
    p2 = Chromosome.random(space)
    
    c1, c2 = GeneticOperators.crossover(p1, p2, space, pc=1.0)
    assert isinstance(c1, Chromosome)
    assert isinstance(c2, Chromosome)
    
    mutated = GeneticOperators.mutate(p1, space, pm=1.0)
    assert isinstance(mutated, Chromosome)
    assert 20 <= mutated.genes["n_estimators"] <= 250

def test_clinical_fitness_evaluator_synthetic():
    np.random.seed(42)
    X = np.random.randn(60, 6)
    y = np.random.choice([0, 1], size=60)
    
    evaluator = ClinicalFitnessEvaluator(X, y, model_name="random_forest", n_splits=3)
    space = HyperparameterGeneSpace.get_space("random_forest")
    chrom = Chromosome.random(space)
    
    fitness = evaluator.evaluate(chrom)
    assert isinstance(fitness, float)
    assert 0.0 <= fitness <= 1.0
    assert "f2_score" in chrom.metrics
    assert "recall" in chrom.metrics

def test_multimodel_spaces_and_evaluation():
    np.random.seed(42)
    X = np.random.randn(40, 5)
    y = np.random.choice([0, 1], size=40)

    for m in ["knn", "logistic_regression", "gradient_boosting", "svm", "mlp"]:
        space = HyperparameterGeneSpace.get_space(m)
        chrom = Chromosome.random(space)
        evaluator = ClinicalFitnessEvaluator(X, y, model_name=m, n_splits=2)
        fit = evaluator.evaluate(chrom)
        assert isinstance(fit, float)
        assert fit >= 0.0

def test_visualizer_creation_and_update(tmp_path):
    from app.genetic.hyperopt.visualizer import LiveGeneticVisualizer
    
    vis = LiveGeneticVisualizer(model_name="knn", dataset_name="cancer", total_generations=2, interactive=False)
    history = {
        "generation": [1, 2],
        "best_fitness": [0.85, 0.90],
        "mean_fitness": [0.80, 0.85],
        "diversity_ratio": [1.0, 0.75],
        "best_metrics": [{"recall": 0.88}, {"recall": 0.92}]
    }
    vis.update(history, current_gen=2)
    
    out_file = str(tmp_path / "test_plot.png")
    vis.save(out_file)
    vis.close()
    
    import os
    assert os.path.exists(out_file)
    assert os.path.getsize(out_file) > 1000
