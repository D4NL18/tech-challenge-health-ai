import os
import json
import pickle
import pandas as pd
import numpy as np

# Import required for unpickling the custom transformer
import sys
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

from training_scripts.utils.data_treatment import OutlierCapper

class TabularPredictor:
    def __init__(self):
        self.models = {}
        self.is_loaded = False
        
        self.cancer_cols = ['radius_mean', 'texture_mean', 'compactness_mean', 'concavity_mean', 'concave points_mean', 'radius_se', 'perimeter_se', 'area_se', 'concavity_se', 'radius_worst', 'texture_worst', 'smoothness_worst', 'compactness_worst', 'concavity_worst', 'concave points_worst', 'symmetry_worst']
        self.pcos_cols = [' Age (yrs)', 'Weight (Kg)', 'Height(Cm) ', 'BMI', 'Hb(g/dl)', 'Cycle(R/I)', 'Cycle length(days)', 'Marraige Status (Yrs)', '  I   beta-HCG(mIU/mL)', 'FSH(mIU/mL)', 'LH(mIU/mL)', 'Hip(inch)', 'Waist(inch)', 'TSH (mIU/L)', 'PRL(ng/mL)', 'Vit D3 (ng/mL)', 'PRG(ng/mL)', 'RBS(mg/dl)', 'Weight gain(Y/N)', 'hair growth(Y/N)', 'Skin darkening (Y/N)', 'Fast food (Y/N)', 'Follicle No. (L)', 'Follicle No. (R)', 'Avg. F size (L) (mm)', 'Avg. F size (R) (mm)', 'Endometrium (mm)']

    def load_model(self):
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
                        with open(model_path, "rb") as mf:
                            self.models[disease] = pickle.load(mf)
                        
            print("TabularPredictor: Modelos carregados com sucesso.", list(self.models.keys()))
            self.is_loaded = True
        except Exception as e:
            print("Erro ao carregar modelos tabulares:", e)

    def predict(self, tabular_data: dict, disease: str) -> float:
        """
        Retorna a probabilidade baseada nos dados tabulares estruturados.
        """
        if not self.is_loaded or disease not in self.models:
            print(f"Fallback mock para {disease} - modelo não carregado.")
            return 0.15 # fallback
            
        model = self.models[disease]
        req_cols = self.cancer_cols if disease == "cancer" else self.pcos_cols
        
        # Cria dataframe com colunas na ordem correta, preenchidas com NaN
        df = pd.DataFrame(columns=req_cols)
        df.loc[0] = np.nan
        
        # Preenche com os dados enviados pelo frontend
        for k, v in tabular_data.items():
            if k in df.columns and v is not None:
                df.at[0, k] = float(v)
                
        # Calcula BMI se for pcos e tiver peso/altura
        if disease == 'pcos':
            w = df.at[0, 'Weight (Kg)']
            h = df.at[0, 'Height(Cm) ']
            if not np.isnan(w) and not np.isnan(h) and h > 0:
                df.at[0, 'BMI'] = w / ((h / 100) ** 2)
                
        # Faz a predição (pega a probabilidade da classe positiva: 1 para pcos, 2 para cancer)
        try:
            probs = model.predict_proba(df)
            return float(probs[0][1])
        except Exception as e:
            print("Erro na predição tabular:", e)
            return 0.15

