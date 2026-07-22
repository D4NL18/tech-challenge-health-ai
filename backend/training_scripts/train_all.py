import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, '..'))
if BACKEND_DIR not in sys.path:
    sys.path.append(BACKEND_DIR)

from training_scripts.utils.data_treatment import load_and_treat_pcos, load_and_treat_cancer
from training_scripts.utils.model_builder import build_and_evaluate_model
from training_scripts.models import (
    random_forest, knn, svm, 
    gradient_boosting, logistic_regression, mlp, naive_bayes
)

# Todos os modelos disponíveis para treino
MODELS = [
    random_forest.get_model_config(),
    knn.get_model_config(),
    svm.get_model_config(),
    gradient_boosting.get_model_config(),
    logistic_regression.get_model_config(),
    mlp.get_model_config(),
    naive_bayes.get_model_config()
]

def run_full_pipeline():
    WEIGHTS_DIR = os.path.join(BACKEND_DIR, 'weights')
    os.makedirs(WEIGHTS_DIR, exist_ok=True)
    
    print("==========================================")
    print(" 1. CARREGAMENTO E TRATAMENTO DOS DADOS")
    print("==========================================")
    
    print("-> Carregando dados do PCOS...")
    df_pcos = load_and_treat_pcos()
    if 'PCOS (Y/N)' in df_pcos.columns:
        df_pcos = df_pcos.rename(columns={'PCOS (Y/N)': 'DIAGNOSTICO_FINAL'})
    
    print("-> Carregando dados de Câncer de Mama...")
    df_cancer = load_and_treat_cancer()
    if 'diagnosis' in df_cancer.columns:
        df_cancer = df_cancer.rename(columns={'diagnosis': 'DIAGNOSTICO_FINAL'})
        df_cancer['DIAGNOSTICO_FINAL'] = df_cancer['DIAGNOSTICO_FINAL'].map({'B': 0, 'M': 2})
    df_cancer = df_cancer.dropna(subset=['DIAGNOSTICO_FINAL'])

    print("\n==========================================")
    print(" 2. TREINAMENTO DOS MODELOS")
    print("==========================================")

    for model_config in MODELS:
        classifier = model_config['classifier']
        param_grid = model_config['param_grid']
        model_name = model_config['model_name']
        
        # Treina e avalia para PCOS
        build_and_evaluate_model(
            df=df_pcos, 
            target_col='DIAGNOSTICO_FINAL', 
            disease_name='PCOS', 
            output_dir=WEIGHTS_DIR, 
            model_name=model_name,
            classifier=classifier, 
            param_grid=param_grid
        )
        
        # Treina e avalia para Câncer de Mama
        build_and_evaluate_model(
            df=df_cancer, 
            target_col='DIAGNOSTICO_FINAL', 
            disease_name='Câncer de Mama', 
            output_dir=WEIGHTS_DIR, 
            model_name=model_name,
            classifier=classifier, 
            param_grid=param_grid
        )
        
    print("\n==========================================")
    print("-> TREINAMENTO DE TODOS OS MODELOS CONCLUÍDO!")
    print("==========================================")

if __name__ == "__main__":
    run_full_pipeline()
