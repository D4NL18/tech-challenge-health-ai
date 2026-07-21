import os
# import xgboost as xgb
# from sklearn.model_selection import train_test_split
# import pickle

def run_tabular_training():
    """
    Este é um script de exemplo para o treinamento de Machine Learning LOCAL.
    Ele foi colocado nesta pasta (training_scripts/) apenas por motivos de
    histórico de estudo e NÃO fará parte da inferência do servidor FastAPI.
    """
    print("Iniciando treinamento do Modelo Tabular (Estudos Locais)...")
    
    # 1. Carregar dataset (ex: CSV local)
    # df = pd.read_csv("dataset_anamnese.csv")
    
    # 2. Treinar modelo
    # model = xgb.XGBClassifier()
    # model.fit(X_train, y_train)
    
    # 3. Exportar pesos para a pasta de weights da API
    # output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'app', 'weights'))
    # os.makedirs(output_dir, exist_ok=True)
    # with open(f"{output_dir}/modelo_tabular.pkl", "wb") as f:
    #     pickle.dump(model, f)
        
    print("Treinamento finalizado! Pesos prontos para serem usados pelo FastAPI.")

if __name__ == "__main__":
    run_tabular_training()
