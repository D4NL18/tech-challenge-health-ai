import os
import json
from app.ml.tabular import TabularPredictor
from app.ml.text import TextPredictor
from app.ml.vision import VisionPredictor
from app.ml.ensemble import EnsemblePredictor
from app.models.schemas import AnamnesisPayload

class InferenceService:
    def __init__(self):
        self.tabular_model = TabularPredictor()
        self.text_model = TextPredictor()
        self.vision_model = VisionPredictor()
        self.ensemble_model = EnsemblePredictor()

    def load_all_models(self):
        """
        Carrega os pesos (arquivos físicos) de todos os modelos.
        """
        self.tabular_model.load_model()
        self.text_model.load_model()
        self.vision_model.load_model()
        self.ensemble_model.load_model()
        
    def _get_active_model(self, disease: str) -> str:
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        active_models_path = os.path.join(base_dir, "weights", "active_models.json")
        try:
            if os.path.exists(active_models_path):
                with open(active_models_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return data.get(disease, "random_forest")
        except Exception:
            pass
        return "random_forest"

    def analyze_full_anamnesis(self, payload: AnamnesisPayload, image_bytes: bytes = None) -> dict:
        """
        Orquestra a passagem dos dados pelos modelos e retorna o diagnóstico final.
        """
        # 1. Tabular (Modelo Treinado)
        tab_score = self.tabular_model.predict(
            tabular_data=payload.tabular_data or {},
            disease=payload.disease
        )

        # 2. Texto (ClinicalBERT)
        txt_score = self.text_model.predict(
            text=payload.symptoms
        )

        # 3. Visão (MobileNet)
        vis_score = None
        if image_bytes:
            vis_score = self.vision_model.predict(image_bytes=image_bytes)

        # 4. Ensemble (Regressão Logística final)
        final_result = self.ensemble_model.predict(
            tabular_score=tab_score,
            text_score=txt_score,
            vision_score=vis_score
        )
        
        # O modelo utilizado vem do config
        disease = payload.disease
            
        active_model = self._get_active_model(disease)
        
        final_result["model_used"] = active_model
        final_result["description"] = f"{final_result['description']} [Predição realizada pelo modelo ativo: {active_model.upper()}]"
        
        return final_result

# Instância Singleton do serviço (será injetada pelo router ou importada)
inference_service = InferenceService()
