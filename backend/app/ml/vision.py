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
    Aplica CLAHE (Contrast Limited Adaptive Histogram Equalization) para
    realçar microcalcificações e estruturas nas mamografias.
    """
    if len(img_np.shape) == 3:
        img_np = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
    
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    clahe_img = clahe.apply(img_np)
    
    # Converter de volta para RGB (necessário para ResNet, DenseNet, etc)
    clahe_img = cv2.cvtColor(clahe_img, cv2.COLOR_GRAY2RGB)
    return clahe_img

def auto_crop_breast(img_np):
    """
    Remove o fundo preto excessivo isolando apenas o tecido mamário.
    """
    gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY) if len(img_np.shape) == 3 else img_np
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
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.transform = transforms.Compose([
            transforms.Resize((512, 512)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])

    def load_model(self):
        try:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            active_models_path = os.path.join(base_dir, "weights", "active_models.json")
            
            model_name = "resnet50"
            if os.path.exists(active_models_path):
                with open(active_models_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    model_name = data.get("vision_cancer", "resnet50")
                    
            model_path = os.path.join(base_dir, "weights", f"modelo_{model_name}_cancer.pth")
            
            # Precisamos da arquitetura para carregar os pesos
            import sys
            if base_dir not in sys.path:
                sys.path.append(base_dir)
                
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

            self.model = model_config['model']
            
            # Carregar pesos no device correto
            state_dict = torch.load(model_path, map_location=self.device)
            self.model.load_state_dict(state_dict)
            self.model.to(self.device)
            self.model.eval()
            
            self.is_loaded = True
            print(f"VisionPredictor: Modelo CNN ({model_name}) carregado com sucesso.")
        except Exception as e:
            print(f"VisionPredictor: Falha ao carregar modelo de visão: {e}")
            self.is_loaded = False

    def predict(self, image_bytes: bytes) -> float:
        """
        Recebe a imagem em bytes e retorna a probabilidade baseada na visão computacional.
        """
        if not self.is_loaded:
            # Fallback seguro para não estourar erro 500
            print("VisionPredictor: Modelo de Visão não carregado, ignorando inferência.")
            return None
            
        try:
            # Decodificar imagem
            img_np = np.frombuffer(image_bytes, np.uint8)
            img = cv2.imdecode(img_np, cv2.IMREAD_COLOR)
            
            if img is None:
                print("VisionPredictor: Não foi possível decodificar a imagem.")
                return None
                
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            
            # Pré-processamento
            img_cropped = auto_crop_breast(img)
            img_clahe = apply_clahe(img_cropped)
            
            # Inferência
            img_pil = Image.fromarray(img_clahe)
            img_tensor = self.transform(img_pil).unsqueeze(0).to(self.device)
            
            with torch.no_grad():
                output = self.model(img_tensor)
                prob = torch.sigmoid(output).item()
                
            return prob
        except Exception as e:
            print(f"VisionPredictor erro durante a predição: {e}")
            return None
