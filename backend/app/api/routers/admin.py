import os
import glob
import json
import jwt
from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import FileResponse
from pydantic import BaseModel
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin")
JWT_SECRET = os.getenv("JWT_SECRET", "super-secret-key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 120

router = APIRouter(prefix="/admin", tags=["Admin Panel"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="admin/login")

class Token(BaseModel):
    access_token: str
    token_type: str

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta if expires_delta else timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_SECRET, algorithm=ALGORITHM)

async def get_current_admin(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token inválido ou expirado",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None or username != ADMIN_USERNAME:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
    return username

@router.post("/login", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    if form_data.username != ADMIN_USERNAME or form_data.password != ADMIN_PASSWORD:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(
        data={"sub": form_data.username}, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/metrics")
async def get_all_metrics(admin: str = Depends(get_current_admin)):
    """
    Lê todos os JSON de métricas em backend/weights/metrics e os compila para o frontend
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    metrics_dir = os.path.join(base_dir, "weights", "metrics")
    
    if not os.path.exists(metrics_dir):
        return {"data": []}
        
    json_files = glob.glob(os.path.join(metrics_dir, "*.json"))
    results = []
    
    for file_path in json_files:
        filename = os.path.basename(file_path)
        # O padrão é metricas_nome_do_modelo_doenca.json
        # Ex: metricas_random_forest_cancer.json
        parts = filename.replace(".json", "").split("_")
        
        # Encontrando se é pcos ou cancer
        disease = "pcos" if "pcos" in parts else "cancer" if "cancer" in parts else "unknown"
        
        # Extraindo o nome do modelo
        if disease != "unknown":
            model_parts = parts[1:parts.index(disease)]
            model_name = "_".join(model_parts)
        else:
            model_name = "_".join(parts[1:])
            
        if disease == "cancer" and model_name in ["resnet50", "densenet121", "efficientnet_b2"]:
            disease = "vision_cancer"
            
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                
            # Garante que a acurácia global esteja presente para os modelos de visão
            if "accuracy" in data and "accuracy_global" not in data:
                data["accuracy_global"] = data["accuracy"]
                
            results.append({
                "model_name": model_name,
                "disease": disease,
                "metrics": data
            })
        except Exception as e:
            continue
            
    return {"data": results}

@router.get("/matrix/{filename}")
async def get_matrix_image(filename: str, admin: str = Depends(get_current_admin)):
    """
    Retorna o arquivo de imagem da matriz de confusão.
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    matrix_dir = os.path.join(base_dir, "weights", "matrix")
    file_path = os.path.join(matrix_dir, filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Matriz não encontrada")
        
    return FileResponse(file_path, media_type="image/png")

class ActiveModelUpdate(BaseModel):
    disease: str
    model_name: str

@router.get("/active-models")
async def get_active_models():
    """
    Retorna os modelos atualmente ativos lendo o json em weights/active_models.json
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    active_models_path = os.path.join(base_dir, "weights", "active_models.json")
    
    if not os.path.exists(active_models_path):
        return {"pcos": "random_forest", "cancer": "random_forest", "vision_cancer": "resnet50", "llm": "gemini"}
        
    try:
        with open(active_models_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            # Garante que vision_cancer e llm existam se o JSON for antigo
            if "vision_cancer" not in data:
                data["vision_cancer"] = "resnet50"
            if "llm" not in data:
                data["llm"] = "gemini"
            return data
    except Exception:
        return {"pcos": "random_forest", "cancer": "random_forest", "vision_cancer": "resnet50", "llm": "gemini"}

@router.post("/active-models")
async def set_active_model(update: ActiveModelUpdate, admin: str = Depends(get_current_admin)):
    """
    Atualiza o modelo ativo para uma doença no JSON local.
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    active_models_path = os.path.join(base_dir, "weights", "active_models.json")
    
    # Tenta carregar o existente
    active_models = {"pcos": "random_forest", "cancer": "random_forest", "vision_cancer": "resnet50", "llm": "gemini"}
    if os.path.exists(active_models_path):
        try:
            with open(active_models_path, "r", encoding="utf-8") as f:
                loaded_models = json.load(f)
                active_models.update(loaded_models)
        except Exception:
            pass
            
    # Garantir que a lista de doenças permitidas inclua vision_cancer e llm
    valid_diseases = ["pcos", "cancer", "vision_cancer", "llm"]
            
    # Atualiza
    if update.disease in valid_diseases:
        active_models[update.disease] = update.model_name
        
        # Salva
        try:
            with open(active_models_path, "w", encoding="utf-8") as f:
                json.dump(active_models, f, indent=2)
            return {"status": "success", "active_models": active_models}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Erro ao salvar: {str(e)}")
    else:
        raise HTTPException(status_code=400, detail="Doença inválida")
