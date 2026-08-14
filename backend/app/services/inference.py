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
        default_model = "gemini" if disease == "llm" else "resnet50" if disease == "vision_cancer" else "random_forest"
        try:
            if os.path.exists(active_models_path):
                with open(active_models_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return data.get(disease, default_model)
        except Exception:
            pass
        return default_model

    def analyze_full_anamnesis(self, payload: AnamnesisPayload, image_bytes: bytes = None) -> dict:
        """
        Orquestra a passagem dos dados pelos modelos e retorna o diagnóstico final.
        """
        disease = payload.disease
        active_model = self._get_active_model(disease)
        active_llm = self._get_active_model("llm")

        # 1. Tabular (Modelo Treinado)
        tab_score = self.tabular_model.predict(
            tabular_data=payload.tabular_data or {},
            disease=disease
        )

        # 2. Texto (LLM Generativa)
        txt_score = None
        if payload.open_text:
            txt_score = self.text_model.predict(
                text=payload.open_text,
                disease=disease,
                active_llm=active_llm
            )

        # 3. Visão (ResNet/DenseNet)
        vis_score = None
        if image_bytes:
            vis_score = self.vision_model.predict(image_bytes=image_bytes)

        # 4. Ensemble (Lógica de pesos atualizada)
        final_result = self.ensemble_model.predict(
            tabular_score=tab_score,
            text_score=txt_score,
            vision_score=vis_score
        )
        
        final_result["model_used"] = active_model
        
        return final_result

# Instância Singleton do serviço (será injetada pelo router ou importada)
inference_service = InferenceService()
