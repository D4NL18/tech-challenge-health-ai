import torch.nn as nn
from torchvision import models
from torchvision.models import EfficientNet_B2_Weights

def get_model_config():
    """
    Retorna a arquitetura EfficientNet-B2 configurada para classificação binária.
    """
    model = models.efficientnet_b2(weights=EfficientNet_B2_Weights.DEFAULT)
    
    # Ajustar a última camada para Classificação Binária (Benigno vs Maligno)
    num_ftrs = model.classifier[1].in_features
    model.classifier[1] = nn.Sequential(
        nn.Dropout(0.5),
        nn.Linear(num_ftrs, 1) # 1 neurônio de saída 
    )
    
    return {
        'model_name': 'efficientnet_b2',
        'model': model,
        'lr': 1e-4,
        'weight_decay': 1e-4
    }
