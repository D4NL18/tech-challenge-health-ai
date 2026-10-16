"""
Módulo de Representação Cromossômica para Hiperparâmetros (P-010).
Permite codificação híbrida: genes inteiros, reais (contínuos/logarítmicos) e categóricos.
"""

import random
import numpy as np
from typing import Dict, Any, List

class HyperparameterGeneSpace:
    """
    Define os limites e tipos de genes para os classificadores clínicos.
    """
    @staticmethod
    def get_space(model_name: str) -> Dict[str, Dict[str, Any]]:
        if model_name in ["random_forest", "Random Forest"]:
            return {
                "n_estimators": {"type": "int", "bounds": (20, 250)},
                "max_depth": {"type": "int_or_none", "bounds": (3, 25)},
                "min_samples_split": {"type": "int", "bounds": (2, 15)},
                "min_samples_leaf": {"type": "int", "bounds": (1, 8)},
                "criterion": {"type": "cat", "choices": ["gini", "entropy", "log_loss"]}
            }
        elif model_name in ["svm", "SVM"]:
            return {
                "C": {"type": "float_log", "bounds": (0.01, 100.0)},
                "gamma": {"type": "float_log", "bounds": (0.0001, 1.0)},
                "kernel": {"type": "cat", "choices": ["rbf", "linear", "poly", "sigmoid"]}
            }
        elif model_name in ["gradient_boosting", "Gradient Boosting"]:
            return {
                "n_estimators": {"type": "int", "bounds": (30, 200)},
                "learning_rate": {"type": "float", "bounds": (0.01, 0.3)},
                "max_depth": {"type": "int", "bounds": (2, 10)},
                "min_samples_split": {"type": "int", "bounds": (2, 10)}
            }
        elif model_name in ["mlp", "MLP"]:
            return {
                "hidden_layer_1": {"type": "int", "bounds": (16, 128)},
                "alpha": {"type": "float_log", "bounds": (0.00001, 0.01)},
                "learning_rate_init": {"type": "float_log", "bounds": (0.0005, 0.05)}
            }
        elif model_name in ["knn", "KNN"]:
            return {
                "n_neighbors": {"type": "int", "bounds": (1, 30)},
                "weights": {"type": "cat", "choices": ["uniform", "distance"]},
                "metric": {"type": "cat", "choices": ["euclidean", "manhattan", "minkowski"]}
            }
        elif model_name in ["logistic_regression", "Logistic Regression"]:
            return {
                "C": {"type": "float_log", "bounds": (0.01, 100.0)},
                "solver": {"type": "cat", "choices": ["lbfgs", "liblinear"]},
                "max_iter": {"type": "int", "bounds": (100, 500)}
            }
        else:
            # Default fallback para árvores
            return {
                "n_estimators": {"type": "int", "bounds": (20, 150)},
                "max_depth": {"type": "int", "bounds": (3, 15)}
            }

class Chromosome:
    """
    Representa um indivíduo da população com seus genes (hiperparâmetros) e fitness associado.
    """
    def __init__(self, genes: Dict[str, Any], fitness: float = 0.0):
        self.genes = genes
        self.fitness = fitness
        self.metrics = {}  # {accuracy, recall, f1, f2, roc_auc}

    @classmethod
    def random(cls, space: Dict[str, Dict[str, Any]]) -> 'Chromosome':
        genes = {}
        for gene_name, spec in space.items():
            gtype = spec["type"]
            if gtype == "int":
                genes[gene_name] = random.randint(spec["bounds"][0], spec["bounds"][1])
            elif gtype == "int_or_none":
                if random.random() < 0.2:
                    genes[gene_name] = None
                else:
                    genes[gene_name] = random.randint(spec["bounds"][0], spec["bounds"][1])
            elif gtype == "float":
                genes[gene_name] = round(random.uniform(spec["bounds"][0], spec["bounds"][1]), 4)
            elif gtype == "float_log":
                log_min = np.log10(spec["bounds"][0])
                log_max = np.log10(spec["bounds"][1])
                genes[gene_name] = round(float(10 ** random.uniform(log_min, log_max)), 5)
            elif gtype == "cat":
                genes[gene_name] = random.choice(spec["choices"])
        return cls(genes=genes)

    def to_sklearn_params(self, model_name: str) -> Dict[str, Any]:
        """
        Converte o dicionário de genes nos parâmetros oficiais aceitos pelo Scikit-Learn.
        """
        params = dict(self.genes)
        if model_name in ["mlp", "MLP"] and "hidden_layer_1" in params:
            hl1 = params.pop("hidden_layer_1")
            params["hidden_layer_sizes"] = (hl1,)
        return params

    def copy(self) -> 'Chromosome':
        c = Chromosome(genes=dict(self.genes), fitness=self.fitness)
        c.metrics = dict(self.metrics)
        return c
