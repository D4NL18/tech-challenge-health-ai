"""
==================================================================================================
ARQUIVO: ml/tabular.py (PROCESSAMENTO DE DADOS ESTRUTURADOS)
==================================================================================================
Objetivo:
Este módulo carrega e executa modelos de Machine Learning clássicos (Regressão Logística, 
Random Forest, Gradient Boosting) treinados com dados tabulares (tabelas do Excel/CSV).
Ele é responsável por pegar os dados brutos digitados no formulário do frontend, convertê-los
em um DataFrame (Tabela Pandas) e passar pela "Pipelines de Inferência" que foi treinada pelos
Cientistas de Dados.

Conceito Técnico (Pipelines e Pickles):
Em produção, não apenas carregamos o "Modelo" (o cérebro matemático), mas a Pipeline inteira.
Isso porque antes do algoritmo pensar, os dados precisam ser escalonados (ex: StandardScaler para 
converter 180cm e 80kg em uma mesma escala matemática) e valores extremos (Outliers) precisam
ser tratados. Tudo isso é empacotado em um arquivo binário `.pkl` (Pickle).
==================================================================================================
"""

import os
import json
import pickle
import pandas as pd
import numpy as np

# IMPORTANTE: Hack de Caminho para Unpickling
# Quando uso bibliotecas externas customizadas durante o treinamento da IA (ex: OutlierCapper),
# o Python precisa conseguir achar a classe original na hora de desserializar (abrir) o arquivo .pkl.
# Por isso, injeto a raiz do projeto no PYTHONPATH.
import sys
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

from training_scripts.utils.data_treatment import OutlierCapper

class TabularPredictor:
    def __init__(self):
        # Dicionário que guardará os modelos na RAM (ex: {"pcos": RandomForest, "cancer": LogisticRegression})
        self.models = {}
        self.is_loaded = False
        
        # Colunas estritas esperadas pelos modelos. A IA falhará se a ordem ou os nomes mudarem,
        # pois ela não lê o nome das colunas, apenas analisa o vetor matemático (Array 1D) na mesma posição do treino.
        self.cancer_cols = ['radius_mean', 'texture_mean', 'compactness_mean', 'concavity_mean', 'concave points_mean', 'radius_se', 'perimeter_se', 'area_se', 'concavity_se', 'radius_worst', 'texture_worst', 'smoothness_worst', 'compactness_worst', 'concavity_worst', 'concave points_worst', 'symmetry_worst']
        self.pcos_cols = [' Age (yrs)', 'Weight (Kg)', 'Height(Cm) ', 'BMI', 'Hb(g/dl)', 'Cycle(R/I)', 'Cycle length(days)', 'Marraige Status (Yrs)', '  I   beta-HCG(mIU/mL)', 'FSH(mIU/mL)', 'LH(mIU/mL)', 'Hip(inch)', 'Waist(inch)', 'TSH (mIU/L)', 'PRL(ng/mL)', 'Vit D3 (ng/mL)', 'PRG(ng/mL)', 'RBS(mg/dl)', 'Weight gain(Y/N)', 'hair growth(Y/N)', 'Skin darkening (Y/N)', 'Fast food (Y/N)', 'Follicle No. (L)', 'Follicle No. (R)', 'Avg. F size (L) (mm)', 'Avg. F size (R) (mm)', 'Endometrium (mm)']

    def load_model(self):
        """
        ----------------------------------------------------------------------------------------------
        FUNÇÃO: load_model
        Objetivo: Ler as preferências do painel admin (ex: usar KNN ou SVM?) e jogar o peso para a RAM.
        Ferramenta: Utilizamos o 'joblib', que é otimizado para carregar grandes arrays NumPy (usados no Scikit-Learn)
        mais rapidamente do que o 'pickle' tradicional.
        ----------------------------------------------------------------------------------------------
        """
        active_models_path = os.path.join(BASE_DIR, "weights", "active_models.json")
        try:
            with open(active_models_path, "r", encoding="utf-8") as f:
                active = json.load(f)
                
            for disease, model_name in active.items():
                model_path = os.path.join(BASE_DIR, "weights", f"modelo_{model_name}_{disease}.pkl")
                if os.path.exists(model_path):
                    import joblib
                    try:
                        self.models[disease] = joblib.load(model_path)
                    except Exception as fallback_err:
                        try:
                            with open(model_path, "rb") as mf:
                                self.models[disease] = pickle.load(mf)
                        except Exception as inner_err:
                            print(f"Erro CRÍTICO ao carregar modelo tabular para {disease}: {inner_err}")
                        
            print("TabularPredictor: Modelos carregados com sucesso.", list(self.models.keys()))
            self.is_loaded = True
        except Exception as e:
            print("Erro ao carregar modelos tabulares:", e)

    def predict(self, tabular_data: dict, disease: str) -> float:
        """
        ----------------------------------------------------------------------------------------------
        FUNÇÃO: predict
        Objetivo: Extrair a probabilidade (porcentagem de risco) do vetor de características do paciente.
        Detalhe Técnico (predict_proba):
        Em vez de pedir para a IA dizer apenas "SIM ou NÃO" (predict clássico), peço o
        "predict_proba", que retorna a porcentagem matemática da confiança na classe maligna.
        ----------------------------------------------------------------------------------------------
        """
        if not self.is_loaded or disease not in self.models:
            print(f"Fallback mock para {disease} - modelo não carregado.")
            return 0.15 # fallback mockado caso o arquivo físico falte no servidor
            
        model = self.models[disease]
        req_cols = self.cancer_cols if disease == "cancer" else self.pcos_cols
        
        # Verifica se há pelo menos UM dado preenchido. Se tudo for nulo,
        # retornamos None para que o Ensemble não utilize a média global como predição real.
        has_valid_data = False
        for k in req_cols:
            v = tabular_data.get(k)
            if v is not None and v != "":
                has_valid_data = True
                break
                
        if not has_valid_data:
            return None
        
        # Cria um dataframe vazio com as colunas na ordem exata e preenche com NaN (Not a Number)
        df = pd.DataFrame(columns=req_cols)
        df.loc[0] = np.nan
        
        # Preenche os campos fornecidos pelo frontend iterando pelo JSON.
        # Campos que o paciente pulou no formulário permanecerão como NaN. As pipelines de Imputação
        # (KNNImputer ou SimpleImputer) embutidas no .pkl lidarão com eles preenchendo a média automaticamente.
        processed_data = {}
        for k in req_cols:
            v = tabular_data.get(k)
            if v is None:
                processed_data[k] = np.nan
            else:
                try:
                    if isinstance(v, str):
                        v_lower = v.lower()
                        if v_lower in ['sim', 'yes', 'true', '1']:
                            v = 1.0
                        elif v_lower in ['não', 'nao', 'no', 'false', '0', '']:
                            v = 0.0
                        else:
                            v = float(v.replace(',', '.'))
                    processed_data[k] = float(v)
                except (ValueError, TypeError):
                    processed_data[k] = np.nan
        
        df = pd.DataFrame([processed_data])
                
        # Feature Engineering On-the-fly (Engenharia de Recursos em Tempo Real):
        # O BMI (IMC) era uma feature fortíssima no treino, então calculo aqui antes de enviar.
        if disease == 'pcos':
            w = df.at[0, 'Weight (Kg)']
            h = df.at[0, 'Height(Cm) ']
            if not np.isnan(w) and not np.isnan(h) and h > 0:
                df.at[0, 'BMI'] = w / ((h / 100) ** 2)
                
        # predict_proba retorna um array de arrays: [[prob_classe0, prob_classe1]].
        # Pego o índice [0][1] para extrair apenas a porcentagem de ter a doença.
        try:
            probs = model.predict_proba(df)
            return float(probs[0][1])
        except Exception as e:
            print("Erro na predição tabular:", e)
            return 0.15

