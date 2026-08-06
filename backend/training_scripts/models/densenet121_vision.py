import torch.nn as nn
from torchvision import models
from torchvision.models import DenseNet121_Weights

def get_model_config():
    """
    Retorna a arquitetura DenseNet-121 configurada para classificação binária.
    """
    model = models.densenet121(weights=DenseNet121_Weights.DEFAULT)
    
    # Ajustar a última camada para Classificação Binária (Benigno vs Maligno)
    num_ftrs = model.classifier.in_features
    model.classifier = nn.Sequential(
        nn.Dropout(0.5),
        nn.Linear(num_ftrs, 1) # 1 neurônio de saída 
    )
    
    return {
        'model_name': 'densenet121',
        'model': model,
        'lr': 1e-4,
        'weight_decay': 1e-4
    }
