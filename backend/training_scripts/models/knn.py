from sklearn.neighbors import KNeighborsClassifier

def get_model_config():
    """
    Retorna as configurações do classificador KNN e sua grade de hiperparâmetros.
    """
    return {
        'model_name': 'knn',
        'classifier': KNeighborsClassifier(),
        'param_grid': {
            'classifier__n_neighbors': [3, 5, 7, 9, 11],
            'classifier__weights': ['uniform', 'distance'],
            'classifier__metric': ['euclidean', 'manhattan']
        }
    }