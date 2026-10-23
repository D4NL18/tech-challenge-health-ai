# 5. MLOps and Model Training

*Read this in other languages: [English](5-mlops-training.md) | [Português](../docs/5-mlops-treinamento.md)*

This document details the lifecycle of Machine Learning models in this project. It answers the question: *"How does a model transition from an offline data experiment to a reliable software product running in production?"*

Since I handle both the **Data Scientist** and **Software Engineer** roles, I physically separated these responsibilities in the codebase to prevent conflation of experimental code with runtime services.

---

## 5.1. The Separation: `training_scripts/` vs `app/ml/`

Machine learning code exists in two distinct project locations:

1.  **`training_scripts/` Folder (The Laboratory):**
    *   This is the offline data science environment.
    *   These scripts run exclusively on local development machines or cloud compute nodes (e.g., Google Colab with GPUs).
    *   They clean raw datasets, perform exploratory data analysis, evaluate search spaces, and execute evolutionary training algorithms.
    *   *Important:* The production FastAPI container **never** executes this folder.

2.  **`app/ml/` Folder (The Factory):**
    *   This is the production software engineering runtime.
    *   Models here are completely trained and frozen.
    *   Classes simply deserialize pretrained weights, apply input validation, and compute fast probabilistic inference via `predict_proba()`.
    *   This is the online environment deployed to Google Cloud Run.

---

## 5.2. Serialization and Exporting (Creating Model Weights)
Once training finishes and evaluation metrics satisfy acceptance criteria, model artifacts are serialized for deployment:

1.  **Tabular Pipelines (Random Forest, XGBoost, Scikit-Learn):**
    The complete preprocessing and estimator pipeline is saved into binary `.pkl` files using `joblib` or `pickle` (e.g., `modelo_pcos.pkl`, `modelo_random_forest_cancer_genetic.pkl`). This bundles both normalization scalers and decision tree thresholds.
2.  **Deep Learning Models (PyTorch):**
    Model state dictionaries containing trained neural weight matrices are saved into `.pth` files (e.g., `modelo_resnet_cancer.pth`).

---

## 5.3. The Bridge: `weights/` Folder
To deploy models, the serialized `.pkl` and `.pth` files are stored in `backend/weights/` (and mirrored in `backend/app/weights/`).

When FastAPI starts up on Cloud Run, the Lifespan event handler loads these files into RAM once, connecting the Data Science experimentation pipeline directly to backend API services.

---

## 5.4. Hyperparameter Calibration via Genetic Algorithms (Phase 2)
**Reference Script:** `backend/training_scripts/train_genetic_hyperopt.py`

In Phase 2, we replaced rigid, computationally expensive GridSearch with a **Bio-Inspired Genetic Algorithm** (`app/genetic/hyperopt/optimizer.py`), offering two operational CLI modes:

1. **Benchmark Mode (`--mode benchmark`):**
   Executes the 3 official experiments required by the challenge (Quick, Balanced, Robust), benchmarks against the Phase 1 Baseline, plots convergence curves, and exports `backend/weights/genetic_experiments_results.json` for direct consumption by the Admin Dashboard.
   ```bash
   python training_scripts/train_genetic_hyperopt.py --mode benchmark
   ```

2. **Multimodel Clinical Mode (`--mode multimodel`):**
   Enables evolutionary tuning across 6 tabular classifier families (`random_forest`, `gradient_boosting`, `svm`, `knn`, `logistic_regression`, `mlp`) on either or both clinical datasets (`cancer`, `pcos`), with real-time interactive convergence visualization via `--live-plot`.
   ```bash
   python training_scripts/train_genetic_hyperopt.py --mode multimodel --model all --disease both --pop 30 --gen 15 --live-plot
   ```

- **Hybrid Multi-Type Chromosome:** Encodes discrete integers (`int`, e.g., `n_estimators`), nullable integers (`int_or_none`, e.g., `max_depth`), continuous floats, base-10 logarithmic floats (`float_log`, e.g., $C$, $\gamma$, `learning_rate` between $10^{-4}$ and $10^{2}$), and categorical parameters (`cat`, e.g., `criterion`, `class_weight`).
- **Genetic Operators:** Tournament Selection ($k=3$) or Roulette with strict Elitism ($E=2$), Hybrid Crossover (Weighted Arithmetic for continuous genes and Uniform for discrete/categorical genes), and Gaussian Mutation with domain boundary reflection.
- **Leakage-Free Cross-Validation:** 5-Fold Stratified Cross-Validation (`StratifiedKFold`) evaluated inside a `Pipeline` where `StandardScaler` is fitted strictly within the training folds of each split.

---

## 5.5. Clinical Objective Function ($F_2$-Score)
In clinical diagnostics (Breast Cancer and PCOS), a **False Negative** (failing to diagnose a sick patient) is catastrophically more hazardous than a False Positive.
Therefore, the fitness function was engineered as:

$$\text{Fitness} = 0.70 \times F_2 + 0.20 \times \text{Recall} + 0.10 \times \text{Accuracy} - \text{Complexity Penalty}$$

Where $F_2$-Score ($\beta = 2$) gives twice the importance to Recall over Precision:

$$F_2 = \frac{5 \times \text{Precision} \times \text{Recall}}{4 \times \text{Precision} + \text{Recall}}$$

---

## 5.6. Results of the 3 Systematic Experiments
We conducted 3 systematic experiments varying population size, generations, mutation rates, and crossover parameters:

| Metric | Baseline (Phase 1 GridSearch) | Exp 1 (Quick / Exploratory) | Exp 2 (Balanced Winner) | Exp 3 (Robust Convergence) |
| :--- | :--- | :--- | :--- | :--- |
| **Population / Generations** | Fixed Grid | 20 / 10 | 40 / 20 | 80 / 30 |
| **$F_2$-Score** | 0.9135 | 0.9527 | **0.9566 (+4.7%)** | 0.9566 |
| **Recall (Malignant)** | 0.9048 | 0.9528 | **0.9576 (+5.8%)** | 0.9576 |
| **Accuracy** | 0.9386 | 0.9631 | **0.9666 (+3.0%)** | 0.9666 |
| **Execution Time** | ~18s | 8.2s | 30.7s | 99.4s |

The winning model from Experiment 2 was serialized into `backend/weights/modelo_random_forest_cancer_genetic.pkl` and full experimental telemetry saved to `backend/weights/genetic_experiments_results.json`.

---

**Next Step:**
Ready to test the system? Access the final module to grab synthetic clinical test cases and verify the routing and automated test suites in [6-test-examples.md](./6-test-examples.md).
