"""
==================================================================================================
train_genetic_hyperopt.py (PROJETO 1 - FASE 2)
==================================================================================================
Objetivo:
Motor central de treinamento e otimização por Algoritmos Genéticos (P-010, P-011, P-012, P-013).
Oferece dois modos de operação:
  1. BENCHMARK FASE 2 (Padrão): Executa os 3 experimentos clássicos (Quick, Balanced, Robust) 
     exigidos pelo Tech Challenge, compara com o Baseline da Fase 1, gera os gráficos individuais 
     e comparativos de convergência, e persiste o relatório oficial para o Painel Admin.
  2. MULTIMODELO CLÍNICO: Permite otimizar qualquer classificador tabular (Random Forest, 
     Gradient Boosting, SVM, KNN, Regressão Logística e MLP) para ambos os datasets (Câncer e SOP), 
     com suporte a visualização interativa em tempo real (--live-plot) e salvamento automático 
     de gráficos em alta resolução para todos os modelos.
==================================================================================================
"""

import os
import sys
import json
import argparse
import joblib
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Configuração de caminhos do projeto
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, '..'))
if BACKEND_DIR not in sys.path:
    sys.path.append(BACKEND_DIR)

from training_scripts.utils.data_treatment import load_and_treat_pcos, load_and_treat_cancer
from app.genetic.hyperopt.optimizer import GeneticHyperparameterOptimizer
from app.genetic.hyperopt.fitness import ClinicalFitnessEvaluator
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, recall_score, f1_score, fbeta_score, roc_auc_score

AVAILABLE_MODELS = [
    "random_forest",
    "gradient_boosting",
    "svm",
    "knn",
    "logistic_regression",
    "mlp"
]

# 3 Configurações Experimentais Exigidas pelo Tech Challenge da Fase 2
EXPERIMENTS_CONFIG = [
    {
        "id": "exp_1_quick",
        "name": "Experimento 1 (Convergência Rápida)",
        "population_size": 20,
        "generations": 10,
        "mutation_rate": 0.05,
        "crossover_rate": 0.70,
        "elitism_count": 1,
        "description": "População pequena e baixa mutação. Avalia convergência acelerada com risco de mínimo local."
    },
    {
        "id": "exp_2_balanced",
        "name": "Experimento 2 (Exploração Balanceada)",
        "population_size": 40,
        "generations": 20,
        "mutation_rate": 0.15,
        "crossover_rate": 0.85,
        "elitism_count": 2,
        "description": "Equilíbrio padrão de exploração e refinamento com elitismo de 2 melhores."
    },
    {
        "id": "exp_3_robust",
        "name": "Experimento 3 (Otimização Robusta / Global)",
        "population_size": 80,
        "generations": 30,
        "mutation_rate": 0.25,
        "crossover_rate": 0.90,
        "elitism_count": 2,
        "description": "Busca global intensiva no hiperespaço com mutação adaptativa e alta diversidade genética."
    }
]

def prepare_cancer_data():
    df_cancer = load_and_treat_cancer()
    if 'diagnosis' in df_cancer.columns:
        df_cancer = df_cancer.rename(columns={'diagnosis': 'DIAGNOSTICO_FINAL'})
        df_cancer['DIAGNOSTICO_FINAL'] = df_cancer['DIAGNOSTICO_FINAL'].map({'B': 0, 'M': 1, 2: 1})
    df_cancer = df_cancer.dropna(subset=['DIAGNOSTICO_FINAL'])
    
    cancer_features = [
        'radius_mean', 'texture_mean', 'compactness_mean', 'concavity_mean', 
        'concave points_mean', 'radius_se', 'perimeter_se', 'area_se', 
        'concavity_se', 'radius_worst', 'texture_worst', 'smoothness_worst', 
        'compactness_worst', 'concavity_worst', 'concave points_worst', 'symmetry_worst'
    ]
    available_cols = [c for c in cancer_features if c in df_cancer.columns]
    X = df_cancer[available_cols].values
    y = df_cancer['DIAGNOSTICO_FINAL'].astype(int).values
    return X, y, available_cols

def prepare_pcos_data():
    df_pcos = load_and_treat_pcos()
    if 'PCOS (Y/N)' in df_pcos.columns:
        df_pcos = df_pcos.rename(columns={'PCOS (Y/N)': 'DIAGNOSTICO_FINAL'})
    df_pcos = df_pcos.dropna(subset=['DIAGNOSTICO_FINAL'])
    
    target_col = 'DIAGNOSTICO_FINAL'
    feature_cols = [c for c in df_pcos.columns if c != target_col]
    
    df_features = df_pcos[feature_cols].copy()
    df_features = df_features.fillna(df_features.median())
    
    X = df_features.values
    y = df_pcos[target_col].astype(int).values
    return X, y, feature_cols

def plot_benchmark_comparison(experiments_results: list, output_path: str):
    """
    Gera um gráfico comparativo consolidando as curvas de convergência dos 3 experimentos.
    """
    try:
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
        fig.suptitle("HealthAI - Comparativo de Convergência dos 3 Experimentos de AG (Fase 2)", fontsize=13, fontweight='bold')

        colors = ["#F59E0B", "#10B981", "#6366F1"]

        for exp, color in zip(experiments_results, colors):
            hist = exp["convergence_history"]
            gens = hist["generation"]
            best_f2 = hist["best_fitness"]
            divs = hist["diversity_ratio"]
            label = f"{exp['name']} (Pop={exp['parameters']['population_size']}, Gen={exp['parameters']['generations']})"

            ax1.plot(gens, best_f2, marker="o", color=color, linewidth=2, label=label)
            ax2.plot(gens, divs, marker="s", linestyle="--", color=color, linewidth=1.8, label=label)

        ax1.set_title("Evolução do Melhor F2-Score Clínico", fontsize=11, fontweight='bold')
        ax1.set_xlabel("Geração")
        ax1.set_ylabel("F2-Score")
        ax1.grid(True, linestyle="--", alpha=0.5)
        ax1.legend(loc="lower right", fontsize=8.5)

        ax2.set_title("Diversidade Genética da População", fontsize=11, fontweight='bold')
        ax2.set_xlabel("Geração")
        ax2.set_ylabel("Proporção de Cromossomos Únicos")
        ax2.grid(True, linestyle="--", alpha=0.5)
        ax2.legend(loc="upper right", fontsize=8.5)

        plt.tight_layout()
        fig.savefig(output_path, dpi=150, bbox_inches="tight")
        plt.close(fig)
        print(f"-> Gráfico comparativo consolidado salvo em: {output_path}")
    except Exception as e:
        print(f"Aviso ao gerar gráfico consolidado: {e}")

def run_fase2_benchmark(live_plot: bool = False):
    """
    Executa o fluxo oficial do Tech Challenge da Fase 2:
    - Baseline da Fase 1
    - 3 Experimentos sistemáticos de AG
    - Plots individuais e comparativos de convergência
    - Persistência em genetic_experiments_results.json e modelo_random_forest_cancer_genetic.pkl
    """
    weights_dir = os.path.join(BACKEND_DIR, "weights")
    plots_dir = os.path.join(weights_dir, "plots")
    os.makedirs(plots_dir, exist_ok=True)

    print("=================================================================")
    print(" EXECUTANDO BENCHMARK OFICIAL DE ALGORITMOS GENÉTICOS (FASE 2)   ")
    print("=================================================================")

    X_cancer, y_cancer, _ = prepare_cancer_data()

    # Linha de Base da Fase 1 (Random Forest Padrão)
    rf_baseline = RandomForestClassifier(random_state=42)
    rf_baseline.fit(X_cancer, y_cancer)
    y_pred_base = rf_baseline.predict(X_cancer)
    baseline_metrics = {
        "accuracy": round(accuracy_score(y_cancer, y_pred_base), 4),
        "recall": round(recall_score(y_cancer, y_pred_base), 4),
        "f1_score": round(f1_score(y_cancer, y_pred_base), 4),
        "f2_score": round(fbeta_score(y_cancer, y_pred_base, beta=2), 4)
    }

    print(f"-> Baseline Fase 1 (Random Forest): Recall={baseline_metrics['recall']} | F2={baseline_metrics['f2_score']} | Acc={baseline_metrics['accuracy']}")

    all_experiments_results = {
        "baseline_fase1": {
            "model": "Random Forest (Default/GridSearch)",
            "metrics": baseline_metrics
        },
        "experiments": []
    }

    best_overall_result = None

    # Executa os 3 Experimentos de AG
    for config in EXPERIMENTS_CONFIG:
        print(f"\n---> Executando: {config['name']} <---")
        exp_plot_path = os.path.join(plots_dir, f"genetic_{config['id']}.png")

        optimizer = GeneticHyperparameterOptimizer(
            X=X_cancer,
            y=y_cancer,
            model_name="random_forest",
            dataset_name="cancer",
            population_size=config["population_size"],
            generations=config["generations"],
            mutation_rate=config["mutation_rate"],
            crossover_rate=config["crossover_rate"],
            elitism_count=config["elitism_count"],
            verbose=True,
            live_plot=live_plot,
            plot_save_path=exp_plot_path
        )

        res = optimizer.run()
        exp_record = {
            "id": config["id"],
            "name": config["name"],
            "description": config["description"],
            "parameters": {
                "population_size": config["population_size"],
                "generations": config["generations"],
                "mutation_rate": config["mutation_rate"],
                "crossover_rate": config["crossover_rate"]
            },
            "elapsed_seconds": res["elapsed_seconds"],
            "best_hyperparameters": res["best_hyperparameters"],
            "best_metrics": res["best_metrics"],
            "convergence_history": res["convergence_history"],
            "plot_path": exp_plot_path
        }
        all_experiments_results["experiments"].append(exp_record)

        if best_overall_result is None or res["best_metrics"]["f2_score"] > best_overall_result["best_metrics"]["f2_score"]:
            best_overall_result = res

    # Gráfico consolidado dos 3 experimentos
    comp_plot_path = os.path.join(plots_dir, "genetic_benchmark_comparison.png")
    plot_benchmark_comparison(all_experiments_results["experiments"], comp_plot_path)

    # Persiste o relatório JSON para o painel Admin
    results_path = os.path.join(weights_dir, "genetic_experiments_results.json")
    with open(results_path, "w", encoding="utf-8") as f:
        json.dump(all_experiments_results, f, indent=2, ensure_ascii=False)
    print(f"\n-> Relatório JSON oficial de benchmark salvo em: {results_path}")

    # Treina o modelo final campeão
    best_params = best_overall_result["best_hyperparameters"]
    final_rf = RandomForestClassifier(random_state=42, **best_params)
    final_rf.fit(X_cancer, y_cancer)

    final_model_path = os.path.join(weights_dir, "modelo_random_forest_cancer_genetic.pkl")
    joblib.dump(final_rf, final_model_path)
    print(f"-> Modelo campeão de AG salvo em: {final_model_path}")

    return all_experiments_results

def run_multimodel_training(
    model_name: str,
    disease_name: str,
    pop_size: int = 30,
    generations: int = 15,
    mutation_rate: float = 0.15,
    crossover_rate: float = 0.85,
    live_plot: bool = False
):
    """
    Otimiza qualquer classificador tabular clínico individualmente,
    salvando o modelo .pkl e o gráfico PNG de convergência.
    """
    weights_dir = os.path.join(BACKEND_DIR, "weights")
    plots_dir = os.path.join(weights_dir, "plots")
    os.makedirs(plots_dir, exist_ok=True)

    if disease_name == "cancer":
        X, y, _ = prepare_cancer_data()
    else:
        X, y, _ = prepare_pcos_data()

    print("\n" + "=" * 70)
    print(f" OTIMIZANDO POR AG: {model_name.upper()} | DATASET: {disease_name.upper()} ")
    print(f" População: {pop_size} | Gerações: {generations} | Mutação: {mutation_rate} | Crossover: {crossover_rate}")
    print(f" Live Plot: {'ATIVO (Janela Dinâmica)' if live_plot else 'DESATIVADO (Headless)'}")
    print("=" * 70)

    plot_path = os.path.join(plots_dir, f"genetic_convergence_{model_name}_{disease_name}.png")

    optimizer = GeneticHyperparameterOptimizer(
        X=X,
        y=y,
        model_name=model_name,
        dataset_name=disease_name,
        population_size=pop_size,
        generations=generations,
        mutation_rate=mutation_rate,
        crossover_rate=crossover_rate,
        elitism_count=2,
        verbose=True,
        live_plot=live_plot,
        plot_save_path=plot_path
    )

    result = optimizer.run()

    # Treina o modelo final campeão
    evaluator = ClinicalFitnessEvaluator(X, y, model_name)
    best_params = result["best_hyperparameters"]
    final_clf = evaluator._instantiate_model(best_params)
    final_clf.fit(X, y)

    model_path = os.path.join(weights_dir, f"modelo_{model_name}_{disease_name}_genetic.pkl")
    joblib.dump(final_clf, model_path)
    print(f"-> Modelo campeão salvo com sucesso: {model_path}")
    print(f"-> Gráfico de convergência salvo em: {plot_path}")

    return {
        "model_name": model_name,
        "disease": disease_name,
        "best_hyperparameters": best_params,
        "best_metrics": result["best_metrics"],
        "elapsed_seconds": result["elapsed_seconds"],
        "plot_path": plot_path,
        "model_path": model_path
    }

def main():
    parser = argparse.ArgumentParser(
        description="Script Unificado de Otimização Genética (HealthAI - Fase 2)",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--mode", type=str, default="benchmark", choices=["benchmark", "multimodel"],
        help="Modo de execução: 'benchmark' (3 experimentos da Fase 2) ou 'multimodel' (otimização de modelos específicos)"
    )
    parser.add_argument(
        "--model", type=str, default=None, choices=AVAILABLE_MODELS + ["all"],
        help="Modelo tabular alvo para o modo multimodel (se omitido e mode=multimodel, treina todos)"
    )
    parser.add_argument(
        "--disease", type=str, default="cancer", choices=["cancer", "pcos", "both"],
        help="Dataset clínico alvo (cancer, pcos ou both)"
    )
    parser.add_argument("--pop", type=int, default=30, help="Tamanho da população genética (padrão: 30)")
    parser.add_argument("--gen", type=int, default=15, help="Número de gerações evolutivas (padrão: 15)")
    parser.add_argument("--mutation", type=float, default=0.15, help="Taxa de mutação genética (padrão: 0.15)")
    parser.add_argument("--crossover", type=float, default=0.85, help="Taxa de crossover (padrão: 0.85)")
    parser.add_argument("--live-plot", action="store_true", help="Exibe a janela gráfica interativa atualizando a cada geração")

    args = parser.parse_args()

    # Se o usuário passou --model explicitamente, muda para o modo multimodel automaticamente
    if args.model is not None and args.mode == "benchmark":
        args.mode = "multimodel"

    if args.mode == "benchmark":
        run_fase2_benchmark(live_plot=args.live_plot)
    else:
        models_to_train = AVAILABLE_MODELS if (args.model in [None, "all"]) else [args.model]
        diseases = ["cancer", "pcos"] if args.disease == "both" else [args.disease]

        all_res = []
        for d in diseases:
            for m in models_to_train:
                res = run_multimodel_training(
                    model_name=m,
                    disease_name=d,
                    pop_size=args.pop,
                    generations=args.gen,
                    mutation_rate=args.mutation,
                    crossover_rate=args.crossover,
                    live_plot=args.live_plot
                )
                all_res.append(res)

        print("\n" + "=" * 70)
        print(" RESUMO CONSOLIDADO DOS MODELOS OTIMIZADOS POR ALGORITMO GENÉTICO ")
        print("=" * 70)
        for r in all_res:
            m = r["best_metrics"]
            print(f"[{r['disease'].upper()}] {r['model_name'].upper():<20} | F2: {m.get('f2_score', 0):.4f} | Recall: {m.get('recall', 0):.4f} | Acc: {m.get('accuracy', 0):.4f} | Tempo: {r['elapsed_seconds']}s")

    print("\nExecução unificada finalizada com sucesso!")

if __name__ == "__main__":
    main()
