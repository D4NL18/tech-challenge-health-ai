from sklearn.ensemble import GradientBoostingClassifier

def get_model_config():
    """
    Retorna as configurações do classificador Gradient Boosting 
    e sua grade de hiperparâmetros.
    """
    return {
        'model_name': 'gradient_boosting',
        'classifier': GradientBoostingClassifier(random_state=42),
        'param_grid': {
            'classifier__n_estimators': [100, 200],         # Número de árvores sequenciais
            'classifier__learning_rate': [0.01, 0.1, 0.2],  # Taxa de aprendizado
            'classifier__max_depth': [3, 5, 7]              # Profundidade máxima de cada árvore
        }
    }
