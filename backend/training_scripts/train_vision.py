import os
import sys
import gc
import torch

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, '..'))
if BACKEND_DIR not in sys.path:
    sys.path.append(BACKEND_DIR)

from training_scripts.utils.vision_data_treatment import get_vision_dataloaders
from training_scripts.utils.vision_model_builder import build_and_evaluate_vision_model
from training_scripts.models import resnet50_vision, densenet121_vision, efficientnet_b2_vision

# guardamos apenas a referência da função que cria o modelo.
MODEL_BUILDERS = [
    resnet50_vision.get_model_config,
    densenet121_vision.get_model_config,
    efficientnet_b2_vision.get_model_config
]

def run_full_vision_pipeline(epochs=3, batch_size=4):
    print("==========================================")
    print(" INICIANDO PIPELINE MODULAR DE VISÃO COMPUTACIONAL ")
    print("==========================================")
    
    print("\n[1/3] Carregando e Pré-processando Dataset DICOM...")
    train_loader, test_loader, y_test = get_vision_dataloaders(batch_size=batch_size)
    
    print("\n[2/3] Iniciando Treinamento e Otimização para cada arquitetura CNN...")
    
    for build_func in MODEL_BUILDERS:
        try:
            model_config = build_func()
            
            build_and_evaluate_vision_model(
                model_config=model_config,
                train_loader=train_loader,
                test_loader=test_loader,
                y_test=y_test,
                epochs=epochs
            )
            
            # Limpeza rigorosa da VRAM da Placa de Vídeo após treinar o modelo
            del model_config['model']
            del model_config
            gc.collect()
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
                
        except Exception as e:
            print(f"Erro ao processar modelo: {e}")

    print("\n[3/3] Pipeline Concluído! Todos os modelos e matrizes de confusão foram salvos com sucesso.")


if __name__ == "__main__":
    run_full_vision_pipeline(epochs=30, batch_size=16)
