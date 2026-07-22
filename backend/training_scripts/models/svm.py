from sklearn.svm import SVC

def get_model_config():
    """
    Retorna as configurações do classificador SVM (Support Vector Machine) 
    e sua grade de hiperparâmetros.
    """
    return {
        'model_name': 'svm',
        # O probability=True é crucial para o ROC-AUC funcionar, pois o SVM por padrão não emite probabilidades.
        'classifier': SVC(probability=True, random_state=42, class_weight='balanced'),
        'param_grid': {
            'classifier__C': [0.1, 1, 10],            # Custo do erro (Regularização)
            'classifier__kernel': ['linear', 'rbf'],  # Linear vs Curvas complexas
            'classifier__gamma': ['scale', 'auto']    # Influência de um único ponto de treino
        }
    }