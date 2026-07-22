from sklearn.ensemble import RandomForestClassifier

def get_model_config():
    """
    Retorna as configurações do classificador Random Forest e sua grade de hiperparâmetros.
    """
    return {
        'model_name': 'random_forest',
        'classifier': RandomForestClassifier(random_state=42, class_weight='balanced'),
        'param_grid': {
            'classifier__n_estimators': [100, 200],
            'classifier__max_depth': [10, 20, None],
            'classifier__min_samples_split': [2, 5]
        }
    }