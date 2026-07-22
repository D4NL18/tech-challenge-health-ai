import os
import pandas as pd
import numpy as np

def load_and_treat_pcos():
    """
    Carrega o dataset PCOS e aplica os tratamentos de nulos e de colunas.
    Retorna um DataFrame limpo, pronto para ser consumido pelos modelos.
    """
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    ROOT_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, '..', '..', '..'))
    DATASETS_DIR = os.path.join(ROOT_DIR, 'backend', 'datasets')
    pcos_path = os.path.join(DATASETS_DIR, 'PCOS_data_without_infertility.csv')
    
    df = pd.read_csv(pcos_path, sep=';', decimal=',')
    
    # 1. Remover coluna Unnamed: 44 que está toda vazia
    if 'Unnamed: 44' in df.columns:
        df = df.drop(columns=['Unnamed: 44'])
    
    # 2. Remover IDs e números de série que não agregam ao modelo
    cols_to_drop = ['Sl. No', 'Patient File No.']
    
    # 2.1 Remover colunas com baixíssima importância preditiva ou muitos nulos
    low_importance_pcos = [
        'Pimples(Y/N)', 'Pulse rate(bpm) ', 'Blood Group', 'RR (breaths/min)',
        'Hair loss(Y/N)', 'BP _Systolic (mmHg)', 'No. of aborptions',
        'Reg.Exercise(Y/N)', 'AMH(ng/mL)', 'BP _Diastolic (mmHg)',
        'Pregnant(Y/N)', 'II    beta-HCG(mIU/mL)', 'FSH/LH', 'Waist:Hip Ratio'
    ]
    cols_to_drop.extend(low_importance_pcos)
    
    df = df.drop(columns=[c for c in cols_to_drop if c in df.columns])
    
    # 3. Forçar conversão de colunas numéricas (transforma erros como '#NOME?' em NaN)
    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')
        
    # 4. Recalcular BMI devido aos erros do Excel (#NOME?)
    # O cálculo é: Peso (kg) / (Altura (m) ^ 2)
    if 'Weight (Kg)' in df.columns and 'Height(Cm) ' in df.columns and 'BMI' in df.columns:
        df['BMI'] = df['Weight (Kg)'] / ((df['Height(Cm) '] / 100) ** 2)
        
    # 5. Remover apenas as linhas fantasmas baseando-se na coluna alvo
    if 'PCOS (Y/N)' in df.columns:
        df = df.dropna(subset=['PCOS (Y/N)'])
    
    return df

def load_and_treat_cancer():
    """
    Carrega o dataset Câncer de Mama e aplica os tratamentos de colunas.
    Retorna um DataFrame limpo, pronto para ser consumido pelos modelos.
    """
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    ROOT_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, '..', '..', '..'))
    DATASETS_DIR = os.path.join(ROOT_DIR, 'backend', 'datasets')
    cancer_path = os.path.join(DATASETS_DIR, 'Breast_Cancer.csv')
    
    df = pd.read_csv(cancer_path)
    
    # 1. Remover coluna Unnamed: 32 que está toda vazia
    if 'Unnamed: 32' in df.columns:
        df = df.drop(columns=['Unnamed: 32'])
        
    # 2. Remover ID que não agrega ao modelo
    cols_to_drop = ['id']
    
    # 2.1 Remover colunas com baixíssima importância preditiva
    low_importance_cancer = [
        'fractal_dimension_worst', 'smoothness_mean', 'texture_se',
        'compactness_se', 'symmetry_mean', 'fractal_dimension_mean',
        'smoothness_se', 'symmetry_se', 'fractal_dimension_se', 'concave points_se'
    ]
    cols_to_drop.extend(low_importance_cancer)
    
    # 2.2 Tratamento de Colinearidade (remover variáveis redundantes ao raio)
    collinear_cancer = ['perimeter_mean', 'area_mean', 'perimeter_worst', 'area_worst']
    cols_to_drop.extend(collinear_cancer)
    
    df = df.drop(columns=[c for c in cols_to_drop if c in df.columns])
        
    return df

from sklearn.base import BaseEstimator, TransformerMixin

class OutlierCapper(BaseEstimator, TransformerMixin):
    def __init__(self, lower_percentile=0.01, upper_percentile=0.99):
        self.lower_percentile = lower_percentile
        self.upper_percentile = upper_percentile
        
    def fit(self, X, y=None):
        if hasattr(X, 'values'):
            X = X.values
        self.lower_bounds_ = np.nanpercentile(X, self.lower_percentile * 100, axis=0)
        self.upper_bounds_ = np.nanpercentile(X, self.upper_percentile * 100, axis=0)
        return self
        
    def transform(self, X, y=None):
        is_df = hasattr(X, 'columns')
        X_arr = X.values if is_df else X
        X_capped = np.clip(X_arr, self.lower_bounds_, self.upper_bounds_)
        if is_df:
            return pd.DataFrame(X_capped, columns=X.columns, index=X.index)
        return X_capped

def get_preprocessor():
    """
    Retorna as etapas comuns de pré-processamento (Imputação de nulos, Capping e Scaling)
    para serem usadas em pipelines de qualquer modelo.
    """
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import StandardScaler
    from sklearn.impute import KNNImputer
    
    return Pipeline(steps=[
        ('imputer', KNNImputer(n_neighbors=5)),
        ('outlier_capper', OutlierCapper(lower_percentile=0.01, upper_percentile=0.99)),
        ('scaler', StandardScaler())
    ])
