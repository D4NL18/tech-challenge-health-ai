from sklearn.linear_model import LogisticRegression

def get_model_config():
    """
    Retorna as configurações do classificador Regressão Logística 
    e sua grade de hiperparâmetros.
    """
    return {
        'model_name': 'logistic_regression',
        # solver='liblinear' é ótimo para datasets pequenos e lida bem com a penalidade l1 ou l2
        'classifier': LogisticRegression(random_state=42, class_weight='balanced', solver='liblinear'),
        'param_grid': {
            'classifier__C': [0.01, 0.1, 1, 10, 100],  # Força da regularização (inverso de lambda)
            'classifier__penalty': ['l1', 'l2']        # Tipo de penalidade
        }
    }
