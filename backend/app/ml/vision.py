"""
==================================================================================================
ARQUIVO: ml/vision.py (PROCESSAMENTO DE IMAGENS E VISÃO COMPUTACIONAL)
==================================================================================================
Objetivo:
Este módulo carrega e executa as Redes Neurais Convolucionais (CNNs) usando a biblioteca PyTorch.
Seu papel é receber uma imagem médica bruta (Raio-X/Mamografia), pré-processá-la para deixá-la
no formato exato que a IA foi treinada (recortes, contraste, redimensionamento) e então passar
pelos "pesos" matemáticos da CNN para detectar a probabilidade de um tumor maligno.

Arquiteturas Suportadas (Trocáveis via Painel Admin):
1. ResNet50 (Residual Networks): Resolve o problema de "Vanishing Gradient" pulando conexões.
2. DenseNet121: Todas as camadas se conectam com as camadas futuras, reaproveitando features.
3. EfficientNet-B2: Otimiza simultaneamente largura, profundidade e resolução da rede.
==================================================================================================
"""

import os
import io
import json
import cv2
import numpy as np
import torch
from torchvision import transforms
from PIL import Image

def apply_clahe(img_np):
    """
    ----------------------------------------------------------------------------------------------
    FUNÇÃO DE PRÉ-PROCESSAMENTO: apply_clahe
    Objetivo: Melhorar o contraste local de imagens médicas.
    O que é CLAHE? Contrast Limited Adaptive Histogram Equalization. 
    Diferente de clarear a imagem toda (o que pode estourar os brancos), o CLAHE divide a imagem
    em pequenos quadrados (8x8) e melhora o contraste dentro de cada quadrado independentemente.
    Isso é vital em Mamografias para realçar "Microcalcificações" (pontos minúsculos) que podem
    ser o início de um tumor.
    ----------------------------------------------------------------------------------------------
    """
    # OpenCV geralmente espera tons de cinza para operações matemáticas de histograma
    if len(img_np.shape) == 3:
        img_np = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
    
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    clahe_img = clahe.apply(img_np)
    
    # Redes neurais pré-treinadas na ImageNet (como a ResNet) exigem 3 canais de cor (RGB).
    # Então duplico o canal de cinza 3 vezes.
    clahe_img = cv2.cvtColor(clahe_img, cv2.COLOR_GRAY2RGB)
    return clahe_img

def auto_crop_breast(img_np):
    """
    ----------------------------------------------------------------------------------------------
    FUNÇÃO DE PRÉ-PROCESSAMENTO: auto_crop_breast
    Objetivo: Remover fundo preto morto.
    Imagens de Raio-X costumam ter muito espaço preto ao redor do tecido real. 
    Se não cortar isso, a IA vai gastar processamento (e perder resolução útil) analisando o nada.
    Esta função usa contornos (cv2.findContours) para desenhar uma "Caixa" ao redor do maior
    objeto branco (o seio) e corta a imagem nessa caixa.
    ----------------------------------------------------------------------------------------------
    """
    gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY) if len(img_np.shape) == 3 else img_np
    # Treshold (Limiarização): Tudo abaixo de 10 (quase preto) vira 0, tudo acima vira 255 (branco)
    _, thresh = cv2.threshold(gray, 10, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return img_np
    c = max(contours, key=cv2.contourArea)
    x, y, w, h = cv2.boundingRect(c)
    return img_np[y:y+h, x:x+w]

class VisionPredictor:
    def __init__(self):
        self.model = None
        self.is_loaded = False
        # Hardware Acceleration: Se o servidor tiver placa de vídeo da NVIDIA (CUDA), o PyTorch
        # rodará 100x mais rápido. Se não, fará fallback seguro para o Processador (CPU).
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        # Transforms (Padrão ImageNet): 
        # A imagem será espremida para 512x512 pixels e seus valores RGB (0 a 255)
        # serão normalizados baseados nas médias matemáticas do ImageNet.
        self.transform = transforms.Compose([
            transforms.Resize((512, 512)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])

    def load_model(self):
        """
        ----------------------------------------------------------------------------------------------
        FUNÇÃO: load_model
        Objetivo: Instanciar a arquitetura vazia da CNN e depois "Injetar" os Pesos Treinados (.pth).
        Diferente do Scikit-Learn que salva o objeto inteiro em um .pkl, em Deep Learning (PyTorch),
        salvo apenas o "Dicionário de Estados" (matrizes matemáticas enormes). Então preciso
        montar o "Esqueleto" da rede antes de aplicar o estado.
        ----------------------------------------------------------------------------------------------
        """
        try:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            active_models_path = os.path.join(base_dir, "weights", "active_models.json")
            
            model_name = "resnet50"
            if os.path.exists(active_models_path):
                with open(active_models_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    model_name = data.get("vision_cancer", "resnet50")
                    
            model_path = os.path.join(base_dir, "weights", f"modelo_{model_name}_cancer.pth")
            
            # Preciso da arquitetura original para carregar os pesos
            import sys
            if base_dir not in sys.path:
                sys.path.append(base_dir)
                
            # Dinamicamente importa a classe correta baseada no painel admin
            if model_name == "resnet50":
                from training_scripts.models.resnet50_vision import get_model_config
                model_config = get_model_config()
            elif model_name == "densenet121":
                from training_scripts.models.densenet121_vision import get_model_config
                model_config = get_model_config()
            elif model_name == "efficientnet_b2":
                from training_scripts.models.efficientnet_b2_vision import get_model_config
                model_config = get_model_config()
            else:
                raise ValueError(f"Arquitetura de visão {model_name} desconhecida.")

            # Monta o "Esqueleto" vazio
            self.model = model_config['model']
            
            # Carregar os pesos matriciais (State Dict) e joga para a Placa de Vídeo (ou CPU)
            state_dict = torch.load(model_path, map_location=self.device)
            self.model.load_state_dict(state_dict)
            self.model.to(self.device)
            # AVISA a rede que estamos em Produção (Evaluation Mode), desativando camadas de 
            # treinamento como Dropout e BatchNormalization móvel.
            self.model.eval() 
            
            self.is_loaded = True
            print(f"VisionPredictor: Modelo CNN ({model_name}) carregado com sucesso no device {self.device}.")
        except Exception as e:
            print(f"VisionPredictor: Falha ao carregar modelo de visão: {e}")
            self.is_loaded = False

    def predict(self, image_bytes: bytes) -> float:
        """
        ----------------------------------------------------------------------------------------------
        FUNÇÃO: predict
        Objetivo: Fluxo de inferência (Front -> API -> Bytes -> OpenCV -> Pré-Proc -> Tensor -> CNN -> Float)
        ----------------------------------------------------------------------------------------------
        """
        if not self.is_loaded:
            # Fallback seguro para não estourar erro 500 no backend inteiro se apenas a IA de Imagem cair
            print("VisionPredictor: Modelo de Visão não carregado, ignorando inferência.")
            return None
            
        try:
            # 1. Transformar a "Tripa de Bytes" que veio da Internet em uma Matriz NumPy (Imagem em RAM)
            img_np = np.frombuffer(image_bytes, np.uint8)
            img = cv2.imdecode(img_np, cv2.IMREAD_COLOR)
            
            if img is None:
                print("VisionPredictor: Não foi possível decodificar a imagem.")
                return None
                
            # OpenCV usa BGR, mas Redes Neurais preferem RGB
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            
            # 2. Pipelines de Limpeza Visual Médica
            img_cropped = auto_crop_breast(img)
            img_clahe = apply_clahe(img_cropped)
            
            # 3. Conversão para o Mundo PyTorch (Tensors)
            img_pil = Image.fromarray(img_clahe)
            # unsqueeze(0) adiciona a dimensão de "Batch" (Lote). 
            # O PyTorch espera [BatchSize, Canais, Altura, Largura]. No nosso caso, Batch será 1.
            img_tensor = self.transform(img_pil).unsqueeze(0).to(self.device)
            
            # 4. Inferência Direta
            # with torch.no_grad(): Desliga o cálculo de Gradientes matemáticos, poupando absurdamente a Memória RAM.
            with torch.no_grad():
                # Passa a imagem pela rede (Forward Pass)
                output = self.model(img_tensor)
                # O output original é um "Logit" (-infinito a +infinito).
                # A função Sigmoid espreme esse valor para ficar exatamente entre 0.0 e 1.0 (Probabilidade)
                prob = torch.sigmoid(output).item()
                
            return prob
        except Exception as e:
            print(f"VisionPredictor erro durante a predição: {e}")
            return None
