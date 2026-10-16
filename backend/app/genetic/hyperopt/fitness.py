"""
Avaliador Clínico de Fitness (P-011).
Mede a qualidade dos hiperparâmetros usando Validação Cruzada Estratificada (5 Folds),
com foco em sensibilidade médica através da métrica F2-Score (Recall com peso quadruplicado).
"""

import numpy as np
from typing import Dict, Any, Tuple
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import accuracy_score, recall_score, precision_score, f1_score, fbeta_score, roc_auc_score
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.svm import SVC
from sklearn.neural_network import MLPClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from .chromosome import Chromosome

class ClinicalFitnessEvaluator:
    def __init__(self, X: np.ndarray, y: np.ndarray, model_name: str, n_splits: int = 5):
        self.X = X
        self.y = y
        self.model_name = model_name
        self.cv = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=42)

    def _instantiate_model(self, params: Dict[str, Any]):
        """
        Instancia o classificador Scikit-Learn com os parâmetros fornecidos.
        Aplica StandardScaler dentro do fold para modelos baseados em distância/gradiente.
        """
        p = dict(params)
        name = self.model_name.lower()
        if "mlp" in name and "hidden_layer_1" in p:
            hl1 = p.pop("hidden_layer_1")
            p["hidden_layer_sizes"] = (hl1,)

        if "random_forest" in name:
            return RandomForestClassifier(random_state=42, n_jobs=-1, **p)
        elif "svm" in name:
            base = SVC(random_state=42, probability=True, **p)
            return Pipeline([('scaler', StandardScaler()), ('clf', base)])
        elif "gradient_boosting" in name:
            return GradientBoostingClassifier(random_state=42, **p)
        elif "mlp" in name:
            base = MLPClassifier(random_state=42, max_iter=300, **p)
            return Pipeline([('scaler', StandardScaler()), ('clf', base)])
        elif "knn" in name:
            base = KNeighborsClassifier(n_jobs=-1, **p)
            return Pipeline([('scaler', StandardScaler()), ('clf', base)])
        elif "logistic_regression" in name:
            base = LogisticRegression(random_state=42, **p)
            return Pipeline([('scaler', StandardScaler()), ('clf', base)])
        else:
            return RandomForestClassifier(random_state=42, **p)

    def evaluate(self, chromosome: Chromosome) -> float:
        """
        Executa 5-Fold Stratified CV e atribui o F2-Score médio como fitness.
        Também armazena as demais métricas no objeto do cromossomo.
        """
        params = chromosome.to_sklearn_params(self.model_name)
        
        accs, recs, precs, f1s, f2s, aucs = [], [], [], [], [], []

        for train_idx, val_idx in self.cv.split(self.X, self.y):
            X_train, X_val = self.X[train_idx], self.X[val_idx]
            y_train, y_val = self.y[train_idx], self.y[val_idx]

            try:
                clf = self._instantiate_model(params)
                clf.fit(X_train, y_train)
                y_pred = clf.predict(X_val)

                # Métrica clínica principal: F2-score (beta=2 dá 4x mais importância ao recall)
                f2 = fbeta_score(y_val, y_pred, beta=2, zero_division=0)
                rec = recall_score(y_val, y_pred, zero_division=0)
                prec = precision_score(y_val, y_pred, zero_division=0)
                acc = accuracy_score(y_val, y_pred)
                f1 = f1_score(y_val, y_pred, zero_division=0)
                
                try:
                    y_prob = clf.predict_proba(X_val)[:, 1]
                    auc = roc_auc_score(y_val, y_prob)
                except Exception:
                    auc = 0.5

                f2s.append(f2)
                recs.append(rec)
                precs.append(prec)
                accs.append(acc)
                f1s.append(f1)
                aucs.append(auc)

            except Exception as e:
                # Penaliza configurações inválidas
                return 0.0

        if not f2s:
            return 0.0

        mean_f2 = float(np.mean(f2s))
        chromosome.fitness = mean_f2
        chromosome.metrics = {
            "f2_score": round(mean_f2, 4),
            "recall": round(float(np.mean(recs)), 4),
            "precision": round(float(np.mean(precs)), 4),
            "accuracy": round(float(np.mean(accs)), 4),
            "f1_score": round(float(np.mean(f1s)), 4),
            "roc_auc": round(float(np.mean(aucs)), 4)
        }
        return mean_f2
