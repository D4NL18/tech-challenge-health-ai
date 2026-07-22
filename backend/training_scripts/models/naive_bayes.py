from sklearn.naive_bayes import GaussianNB

def get_model_config():
    """
    Retorna as configurações do classificador Naive Bayes Gaussiano.
    """
    return {
        'model_name': 'naive_bayes',
        'classifier': GaussianNB(),
        'param_grid': {
            'classifier__var_smoothing': [1e-9, 1e-8, 1e-7, 1e-6, 1e-5]  # Porção da maior variância de todas as features que é adicionada às variâncias para estabilidade computacional
        }
    }
