import os
import json
import joblib
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, roc_auc_score

def evaluate_and_save_model(best_model, X, X_test, y_test, disease_name, output_dir, file_name, target_names):
    """
    Avalia o modelo treinado, gera métricas (JSON), matriz de confusão (PNG) 
    e exporta o modelo (PKL).
    """
    print("\n[3/4] Realizando Testes e calculando Métricas...")
    y_pred = best_model.predict(X_test)
    
    # Probabilidades para a classe positiva (usado no ROC-AUC)
    y_prob = best_model.predict_proba(X_test)[:, 1]
    
    acc = accuracy_score(y_test, y_pred)
    print(f"\n--- RESULTADOS DAS MÉTRICAS ({disease_name}) ---")
    print(f"-> Acurácia Global: {acc * 100:.2f}%")
    
    try:
        roc_auc_val = roc_auc_score(y_test, y_prob)
        print(f"-> ROC-AUC Score: {roc_auc_val:.4f}")
    except ValueError:
        roc_auc_val = None
        print("-> ROC-AUC Score: Não foi possível calcular.")
        
    print("\n-> Relatório de Classificação Detalhado:")
    print(classification_report(y_test, y_pred, target_names=target_names))
    
    # Matriz de Confusão
    cm = confusion_matrix(y_test, y_pred)
    plt.figure(figsize=(6, 5))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                xticklabels=target_names, yticklabels=target_names)
    plt.title(f'Matriz de Confusão - {disease_name}')
    plt.ylabel('Classe Real (Verdadeira)')
    plt.xlabel('Classe Prevista (Pelo Modelo)')
    
    matrix_dir = os.path.join(output_dir, 'matrix')
    os.makedirs(matrix_dir, exist_ok=True)
    cm_path = os.path.join(matrix_dir, f'matriz_{file_name}.png')
    plt.savefig(cm_path, dpi=300, bbox_inches='tight')
    print(f"      -> Matriz salva como '{os.path.basename(cm_path)}'.")
    plt.close()
    
    # Salvar métricas e importância de features em JSON
    metrics_dir = os.path.join(output_dir, 'metrics')
    os.makedirs(metrics_dir, exist_ok=True)
    report_dict = classification_report(y_test, y_pred, target_names=target_names, output_dict=True)
    report_dict['accuracy_global'] = acc
    report_dict['roc_auc'] = roc_auc_val
    
    # Importância das features
    classifier = best_model.steps[-1][1] if hasattr(best_model, 'steps') else best_model
    
    if hasattr(classifier, 'feature_importances_'):
        importances = classifier.feature_importances_
        features = X.columns
        feature_importance_df = pd.DataFrame({'Feature': features, 'Importance': importances})
        feature_importance_df = feature_importance_df.sort_values(by='Importance', ascending=False)
        
        report_dict['feature_importances'] = feature_importance_df.to_dict(orient='records')
    
    metrics_path = os.path.join(metrics_dir, f'metricas_{file_name}.json')
    with open(metrics_path, 'w', encoding='utf-8') as f:
        json.dump(report_dict, f, indent=4)
    print(f"      -> Métricas salvas como '{os.path.basename(metrics_path)}'.")
    
    print("\n[4/4] Exportando modelo...")
    model_path = os.path.join(output_dir, f"modelo_{file_name}.pkl")
    joblib.dump(best_model, model_path)
        
    print(f"      -> Modelo salvo com sucesso em: {model_path}")
    print(f"-> Pipeline finalizado para {disease_name}!\n")
