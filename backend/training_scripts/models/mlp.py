from sklearn.neural_network import MLPClassifier

def get_model_config():
    """
    Retorna as configurações do classificador MLP (Rede Neural Artificial) 
    e sua grade de hiperparâmetros.
    """
    return {
        'model_name': 'mlp',
        'classifier': MLPClassifier(random_state=42, max_iter=1000),
        'param_grid': {
            'classifier__hidden_layer_sizes': [(50,), (100,), (50, 50)], # Topologia das camadas ocultas
            'classifier__activation': ['relu', 'tanh'],                  # Função de ativação
            'classifier__alpha': [0.0001, 0.001, 0.01],                  # Regularização L2 para evitar overfitting
            'classifier__learning_rate': ['constant', 'adaptive']        # Comportamento da taxa de aprendizado
        }
    }
