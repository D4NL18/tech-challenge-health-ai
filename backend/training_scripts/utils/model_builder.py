import os
from sklearn.model_selection import train_test_split, GridSearchCV
from imblearn.pipeline import Pipeline
from imblearn.over_sampling import SMOTE

from training_scripts.utils.data_treatment import get_preprocessor
from training_scripts.utils.metrics_eval import evaluate_and_save_model

def build_and_evaluate_model(df, target_col, disease_name, output_dir, model_name, classifier, param_grid):
    """
    Função genérica para construir e avaliar modelos.
    Reduz repetição de código (Data Split, Pipeline de SMOTE, GridSearchCV e Avaliação).
    """
    print(f"\n==========================================")
    print(f" TREINAMENTO DO MODELO: {model_name.upper()} ({disease_name})")
    print(f"==========================================")
    
    X = df.drop(columns=[target_col])
    y = df[target_col]
    
    print("[1/4] Separando dados de Treino e Teste...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print("[2/4] Iniciando Treinamento e Otimização de Hiperparâmetros (GridSearch)...")
    preprocessor = get_preprocessor()
    
    pipeline_steps = preprocessor.steps + [
        ('smote', SMOTE(random_state=42)),
        ('classifier', classifier)
    ]
    pipeline = Pipeline(steps=pipeline_steps)
    
    grid_search = GridSearchCV(pipeline, param_grid, cv=5, scoring='accuracy', n_jobs=-1)
    grid_search.fit(X_train, y_train)
    
    best_model = grid_search.best_estimator_
    print(f"      Melhores parâmetros encontrados: {grid_search.best_params_}")
    
    target_names = ['Saudavel (0)', 'PCOS (1)'] if disease_name == 'PCOS' else ['Saudavel (0)', 'Cancer (2)']
    
    # Avaliar e exportar
    file_name_disease = 'pcos' if disease_name == 'PCOS' else 'cancer'
    evaluate_and_save_model(best_model, X, X_test, y_test, disease_name, output_dir, f"{model_name}_{file_name_disease}", target_names)
