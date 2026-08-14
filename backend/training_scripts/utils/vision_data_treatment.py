import os
import cv2
import numpy as np
import pandas as pd
import torch
from torch.utils.data import Dataset, DataLoader, WeightedRandomSampler
from torchvision import transforms
from PIL import Image
from sklearn.model_selection import train_test_split

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, '..', '..'))
DATASET_DIR = os.path.join(BACKEND_DIR, 'datasets', 'Breast_Cancer_images')

def apply_clahe(img_np):
    """
    Aplica CLAHE (Contrast Limited Adaptive Histogram Equalization) para
    realçar microcalcificações e estruturas nas mamografias.
    
    Conceito e Motivação:
    Mamografias geralmente têm baixo contraste inerente, tornando difícil distinguir
    massas sutis e microcalcificações do tecido mamário normal denso.
    O CLAHE divide a imagem em pequenos blocos (tiles) e aplica a equalização
    de histograma localmente. Ele também limita o contraste para evitar a amplificação
    de ruído, comum em imagens médicas, fornecendo um realce de bordas superior
    em comparação com a equalização de histograma global.
    """
    if len(img_np.shape) == 3:
        img_np = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
    
    # clipLimit define o quão agressivo será o contraste. 2.0 é um bom equilíbrio para não gerar artefatos.
    # tileGridSize (8,8) é o tamanho do grid para o processamento local.
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    clahe_img = clahe.apply(img_np)
    
    # Converter de volta para RGB (necessário para ResNet, DenseNet, etc, que esperam 3 canais)
    clahe_img = cv2.cvtColor(clahe_img, cv2.COLOR_GRAY2RGB)
    return clahe_img

def auto_crop_breast(img_np):
    """
    Remove o fundo preto excessivo isolando apenas o tecido mamário.
    
    Conceito e Motivação:
    Muitas imagens médicas vêm com grandes bordas pretas (ar) ao redor da região de interesse.
    Processar essas áreas vazias desperdiça processamento e pode confundir a CNN.
    Esta função utiliza limiarização (threshold) e detecção de contornos para
    identificar a maior massa brilhante (a mama) e faz um recorte (bounding box) exato dela,
    focando a atenção da rede neural no que importa.
    """
    gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY) if len(img_np.shape) == 3 else img_np
    # Cria uma máscara binária separando os pixels escuros (fundo) dos claros (tecido)
    _, thresh = cv2.threshold(gray, 10, 255, cv2.THRESH_BINARY)
    # Encontra os contornos na máscara
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return img_np
    # Assume que o maior contorno encontrado é o tecido mamário
    c = max(contours, key=cv2.contourArea)
    x, y, w, h = cv2.boundingRect(c)
    # Retorna o recorte (crop) da região delimitada pelo retângulo
    return img_np[y:y+h, x:x+w]

class BreastCancerDataset(Dataset):
    def __init__(self, image_paths, labels, transform=None):
        self.image_paths = image_paths
        self.labels = labels
        self.transform = transform

    def __len__(self):
        return len(self.image_paths)

    def __getitem__(self, idx):
        img_path = self.image_paths[idx]
        
        if img_path == "mock":
            img_np = np.random.randint(0, 256, (1024, 1024, 3), dtype=np.uint8)
        else:
            img = Image.open(img_path).convert('RGB')
            img_np = np.array(img)
            
        img_cropped = auto_crop_breast(img_np)
        img_clahe = apply_clahe(img_cropped)
        img_pil = Image.fromarray(img_clahe)
        
        if self.transform:
            img_tensor = self.transform(img_pil)
        else:
            img_tensor = transforms.ToTensor()(img_pil)
            
        label = torch.tensor(self.labels[idx], dtype=torch.float32)
        return img_tensor, label

def load_and_treat_vision_data():
    csv_dir = os.path.join(DATASET_DIR, "csv")
    if not os.path.exists(csv_dir):
        print("-> Dataset real não encontrado ou insuficiente. Gerando dados MOCK para treino...")
        image_paths = ["mock"] * 100
        labels = [0]*80 + [1]*20
        return train_test_split(image_paths, labels, test_size=0.2, stratify=labels, random_state=42)

    desc_files = [
        "mass_case_description_train_set.csv",
        "mass_case_description_test_set.csv",
        "calc_case_description_train_set.csv",
        "calc_case_description_test_set.csv"
    ]
    
    dfs = []
    for f in desc_files:
        f_path = os.path.join(csv_dir, f)
        if os.path.exists(f_path):
            dfs.append(pd.read_csv(f_path))
            
    if not dfs:
        print("-> CSVs não encontrados. Gerando MOCK...")
        return train_test_split(["mock"]*100, [0]*80 + [1]*20, test_size=0.2, random_state=42)
        
    descriptions = pd.concat(dfs, ignore_index=True)
    descriptions['match_key'] = descriptions['patient_id'] + '_' + descriptions['left or right breast'] + '_' + descriptions['image view']

    pathology_map = {}
    for _, row in descriptions.iterrows():
        key = row['match_key']
        pathology = row['pathology']
        if key not in pathology_map:
            pathology_map[key] = pathology
        elif pathology == 'MALIGNANT':
            pathology_map[key] = pathology

    dicom_info = pd.read_csv(os.path.join(csv_dir, "dicom_info.csv"))
    
    image_paths = []
    labels = []
    label_map = {'BENIGN': 0, 'BENIGN_WITHOUT_CALLBACK': 0, 'MALIGNANT': 1}

    for _, row in dicom_info.iterrows():
        if row['SeriesDescription'] != 'cropped images':
            continue
            
        img_path_rel = row['image_path'].replace('CBIS-DDSM/', '').replace('/', os.sep)
        full_path = os.path.join(DATASET_DIR, img_path_rel)
        
        pid = str(row['PatientID'])
        parts = pid.split('_')
        if len(parts) >= 4:
            p_id = parts[1] + '_' + parts[2]
            side = parts[3]
            view = parts[4]
            match_key = f"{p_id}_{side}_{view}"
            
            if match_key in pathology_map:
                patho = pathology_map[match_key]
                if patho in label_map and os.path.exists(full_path):
                    image_paths.append(full_path)
                    labels.append(label_map[patho])

    if len(image_paths) < 10:
        print("-> Dataset real não encontrado ou insuficiente após parsing. Gerando dados MOCK...")
        image_paths = ["mock"] * 100
        labels = [0]*80 + [1]*20
        
    print(f"-> Foram encontradas {len(image_paths)} imagens reais para treinamento.")
    return train_test_split(image_paths, labels, test_size=0.2, stratify=labels, random_state=42)

def get_vision_dataloaders(batch_size=8):
    train_paths, test_paths, y_train, y_test = load_and_treat_vision_data()
    
    # Data Augmentation e Pré-processamento
    # Motivação: Data augmentation gera variações artificiais das imagens (rotações, flips, brilho)
    # para prevenir que a rede neural decore (overfit) as imagens de treino e melhore a generalização
    # para novos pacientes.
    train_transforms = transforms.Compose([
        transforms.Resize((512, 512)), # Padroniza o tamanho da entrada. 512 preserva detalhes finos sem estourar VRAM
        transforms.RandomHorizontalFlip(), # Inverte mamas (espelha dir/esq)
        transforms.RandomVerticalFlip(), # Espelhamento vertical (ajuda em views diferentes)
        transforms.RandomAffine(degrees=15, translate=(0.1, 0.1), scale=(0.9, 1.1)), # Simula pequenos erros de posicionamento na máquina
        transforms.ColorJitter(brightness=0.2, contrast=0.2), # Simula variações na exposição do raio-x
        transforms.ToTensor(), # Converte PIL Image (0-255) para Tensor PyTorch (0.0-1.0)
        # Normalização com as médias e desvios padrão do ImageNet.
        # CRUCIAL: Como usamos arquiteturas pré-treinadas no ImageNet, os tensores devem
        # ter a mesma distribuição estatística que a rede viu originalmente para acelerar a convergência.
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    
    test_transforms = transforms.Compose([
        transforms.Resize((512, 512)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    
    train_dataset = BreastCancerDataset(train_paths, y_train, transform=train_transforms)
    test_dataset = BreastCancerDataset(test_paths, y_test, transform=test_transforms)
    
    # WeightedRandomSampler: Trata o Desbalanceamento de Classes (ex: muitos benignos, poucos malignos)
    # Conceito: Em vez de amostrar sequencialmente as imagens, usamos pesos inversamente proporcionais 
    # à frequência da classe. A rede verá, na média, 50% malignos e 50% benignos por epoch.
    # Evita que a rede fique "preguiçosa" e aprenda apenas a chutar a classe majoritária.
    class_counts = np.bincount(y_train)
    class_weights = 1.0 / class_counts
    sample_weights = [class_weights[int(label)] for label in y_train]
    sampler = WeightedRandomSampler(weights=sample_weights, num_samples=len(sample_weights), replacement=True)
    
    num_workers = 4 if torch.cuda.is_available() else 0
    pin_memory = torch.cuda.is_available()
    
    # Ao usar o sampler, shuffle DEVE ser False
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=False, sampler=sampler, num_workers=num_workers, pin_memory=pin_memory)
    test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False, num_workers=num_workers, pin_memory=pin_memory)
    
    return train_loader, test_loader, y_test
