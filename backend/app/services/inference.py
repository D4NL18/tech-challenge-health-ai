"""
==================================================================================================
ARQUIVO: services/inference.py (CAMADA DE SERVIÇO / ORQUESTRADOR)
==================================================================================================
Objetivo:
Este arquivo atua como o "Cérebro" ou "Maestro" do backend. O Controller de API recebe os dados brutos,
mas é esta classe (`InferenceService`) que decide para quais modelos os dados devem ir, em qual ordem,
e como agregar as respostas.

Padrão de Projeto (Design Pattern):
Uso o padrão 'Facade' (Fachada). O Controller de API não precisa saber como o PyTorch funciona, nem
como a LLM é chamada. Ele simplesmente chama `analyze_full_anamnesis` e recebe a resposta pronta.
==================================================================================================
"""

import os
import json
from app.ml.tabular import TabularPredictor
from app.ml.text import TextPredictor
from app.ml.vision import VisionPredictor
from app.ml.ensemble import EnsemblePredictor
from app.models.schemas import AnamnesisPayload

class InferenceService:
    def __init__(self):
        # Instancia as "Especialidades" da nossa IA
        self.tabular_model = TabularPredictor()
        self.text_model = TextPredictor()
        self.vision_model = VisionPredictor()
        self.ensemble_model = EnsemblePredictor()

    def load_all_models(self):
        """
        ----------------------------------------------------------------------------------------------
        FUNÇÃO: load_all_models
        Objetivo: Chamar o método 'load_model' de cada classe especialista.
        Uso: Chamado exclusivamente pelo 'lifespan' do main.py durante a inicialização do servidor.
        ----------------------------------------------------------------------------------------------
        """
        self.tabular_model.load_model()
        self.text_model.load_model()
        self.vision_model.load_model()
        self.ensemble_model.load_model()
        
    def _get_active_model(self, disease: str) -> str:
        """
        ----------------------------------------------------------------------------------------------
        FUNÇÃO: _get_active_model (Método Privado)
        Objetivo: Descobrir qual modelo o usuário selecionou no "Painel de Administração" do Frontend.
        Detalhe: O painel salva a escolha no arquivo 'weights/active_models.json'. Aqui, leio esse
        arquivo em tempo real para saber se devo usar Gemini ou GPT, Regressão Logística ou Random Forest.
        ----------------------------------------------------------------------------------------------
        """
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        active_models_path = os.path.join(base_dir, "weights", "active_models.json")
        # Fallbacks (Valores padrão caso o arquivo json não exista)
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
        ----------------------------------------------------------------------------------------------
        FUNÇÃO: analyze_full_anamnesis
        Objetivo: O fluxo principal do sistema (Pipeline). Recebe todos os dados e orquestra a predição.
        
        Passo a passo (Pipeline de IA):
        1. Consulta qual modelo tabular e qual LLM estão ativos.
        2. Manda os dados numéricos (ex: Idade, Tamanho do tumor) para o modelo Tabular Clássico.
        3. Manda o texto digitado pelo paciente para o LLM interpretar a gravidade.
        4. Manda o Raio-X (se existir) para a Rede Neural de Visão Computacional.
        5. Passa os 3 resultados individuais para o 'Ensemble', que faz a média final.
        ----------------------------------------------------------------------------------------------
        """
        disease = payload.disease
        active_model = self._get_active_model(disease)
        active_llm = self._get_active_model("llm")

        # 1. Pipeline Tabular (Algoritmos Clássicos: Random Forest, SVM, Regressão)
        tab_score = self.tabular_model.predict(
            tabular_data=payload.tabular_data or {},
            disease=disease
        )

        # 2. Pipeline de NLP (Inteligência Artificial Generativa: Gemini, ChatGPT)
        txt_score = None
        if payload.open_text:
            txt_score = self.text_model.predict(
                text=payload.open_text,
                disease=disease,
                active_llm=active_llm
            )

        # 3. Pipeline de Visão Computacional (Redes Neurais Convolucionais - CNNs)
        vis_score = None
        if image_bytes:
            vis_score = self.vision_model.predict(image_bytes=image_bytes)

        # 4. Pipeline Final (Ensemble Learning)
        # Junta todas as perspectivas ("opiniões") para tomar uma decisão final robusta
        final_result = self.ensemble_model.predict(
            tabular_score=tab_score,
            text_score=txt_score,
            vision_score=vis_score
        )
        
        # Embuto qual modelo foi o "carro chefe" da resposta para o Frontend exibir.
        final_result["model_used"] = active_model
        
        return final_result

# Padrão Singleton: Exporto uma única instância dessa classe para que toda a aplicação
# compartilhe a mesma "memória" e não carregue os modelos gigantes múltiplas vezes.
inference_service = InferenceService()
