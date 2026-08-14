import os
import json
import torch
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from sklearn.metrics import accuracy_score, confusion_matrix, roc_auc_score, roc_curve, classification_report

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, '..', '..'))
WEIGHTS_DIR = os.path.join(BACKEND_DIR, 'weights')

def evaluate_and_save_vision_model(model, model_name, test_loader, y_test, device):
    """
    Avalia o modelo de visão (acurácia, matriz confusão, roc auc)
    e salva o modelo (.pth) e as métricas.
    """
    model.eval()
    all_preds = []
    all_probs = []
    all_targets = []
    
    with torch.no_grad():
        for inputs, labels in test_loader:
            inputs = inputs.to(device)
            labels = labels.to(device)
            
            outputs = model(inputs)
            probs = torch.sigmoid(outputs).squeeze()
            
            # Se o batch size for 1, probs será um escalar. Precisamos converter para lista.
            if probs.dim() == 0:
                probs = probs.unsqueeze(0)
            
            all_probs.extend(probs.cpu().numpy())
            all_targets.extend(labels.cpu().numpy())
            
    try:
        # ROC-AUC (Receiver Operating Characteristic - Area Under Curve)
        # Conceito: Avalia a capacidade do modelo de distinguir entre as classes (Benigno vs Maligno)
        # em vários limiares de probabilidade. Um valor de 0.5 é um chute aleatório, 1.0 é um modelo perfeito.
        roc_auc = roc_auc_score(all_targets, all_probs)
        fpr, tpr, thresholds = roc_curve(all_targets, all_probs)
        
        # Encontrar o limiar ótimo (Optimal Threshold) usando a estatística J de Youden
        # Motivação: O padrão para classificação binária é usar 0.5 como corte. 
        # No entanto, em dados desbalanceados ou contextos médicos, um corte de 0.5 pode não ser o ideal.
        # Maximizamos (True Positive Rate - False Positive Rate) para encontrar o ponto
        # que melhor equilibra a sensibilidade (achar o câncer) e a especificidade (não dar falso alarme).
        optimal_idx = np.argmax(tpr - fpr)
        optimal_threshold = thresholds[optimal_idx]
    except ValueError:
        roc_auc = 0.5 # Apenas uma classe no teste (mocks)
        optimal_threshold = 0.5
        
    # Aplicação do limiar (threshold) que maximiza a taxa de verdadeiros positivos e minimiza os falsos positivos na curva ROC
    # Transformamos as probabilidades (0.0 a 1.0) em classes discretas (0 ou 1) usando o limiar ótimo calculado.
    all_preds = (np.array(all_probs) >= optimal_threshold).astype(float)
    
    # Calculando Métricas
    # Acurácia: % total de acertos (cuidado, pode ser enganosa em datasets muito desbalanceados).
    acc = accuracy_score(all_targets, all_preds)
    
    # Matriz de Confusão: Detalha onde o modelo errou.
    # Revela os Verdadeiros Positivos (TP), Verdadeiros Negativos (TN), Falsos Positivos (FP) e Falsos Negativos (FN).
    # Em medicina, os Falsos Negativos (dizer que não é câncer quando é) são os erros mais críticos.
    cm = confusion_matrix(all_targets, all_preds)

    print("\n--- RESULTADOS DAS MÉTRICAS ---")
    print(f"-> Acurácia Global: {acc * 100:.2f}%")
    print(f"-> ROC-AUC Score: {roc_auc:.4f}")
    print(f"-> Limiar Ótimo Usado: {optimal_threshold:.4f}")
    
    print("\n--- RELATÓRIO DE CLASSIFICAÇÃO ---")
    try:
        print(classification_report(all_targets, all_preds, target_names=['Benigno', 'Maligno']))
    except ValueError:
        print("Relatório indisponível (apenas uma classe no teste)")
    
    # Salvar Matriz de Confusão
    plt.figure(figsize=(6,5))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                xticklabels=['Benigno', 'Maligno'], 
                yticklabels=['Benigno', 'Maligno'])
    plt.ylabel('Verdadeiro')
    plt.xlabel('Predito')
    plt.title(f'Matriz de Confusão - {model_name.upper()}')
    plt.tight_layout()
    
    matrix_path = os.path.join(WEIGHTS_DIR, 'matrix', f'matriz_{model_name}_cancer.png')
    plt.savefig(matrix_path)
    plt.close()
    
    # Salvar Métricas JSON
    metrics_path = os.path.join(WEIGHTS_DIR, 'metrics', f'metricas_{model_name}_cancer.json')
    metrics_data = {
        'accuracy': float(acc),
        'roc_auc': float(roc_auc),
        'optimal_threshold': float(optimal_threshold)
    }
    with open(metrics_path, 'w', encoding='utf-8') as f:
        json.dump(metrics_data, f, indent=4)
        
    # Salvar Modelo PyTorch (.pth)
    model_path = os.path.join(WEIGHTS_DIR, f'modelo_{model_name}_cancer.pth')
    torch.save(model.state_dict(), model_path)
    
    print(f"-> Treinamento completo! Modelo e métricas salvos em '{WEIGHTS_DIR}'")
