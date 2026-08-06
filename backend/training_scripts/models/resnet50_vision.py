import torch.nn as nn
from torchvision import models
from torchvision.models import ResNet50_Weights

def get_model_config():
    """
    Retorna a arquitetura ResNet-50 configurada para classificação binária.
    """
    model = models.resnet50(weights=ResNet50_Weights.DEFAULT)
    
    # Ajustar a última camada para Classificação Binária (Benigno vs Maligno)
    num_ftrs = model.fc.in_features
    model.fc = nn.Sequential(
        nn.Dropout(0.5),
        nn.Linear(num_ftrs, 1) # 1 neurônio de saída 
    )
    
    return {
        'model_name': 'resnet50',
        'model': model,
        'lr': 1e-4,
        'weight_decay': 1e-4
    }
