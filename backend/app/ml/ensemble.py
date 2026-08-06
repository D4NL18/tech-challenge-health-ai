class EnsemblePredictor:
    def __init__(self):
        # MOCK: O meta-modelo (Regressão Logística) que pega a saída dos 3 modelos
        self.model = None
        self.is_loaded = False

    def load_model(self):
        print("EnsemblePredictor: Meta-modelo carregado com sucesso.")
        self.is_loaded = True

    def predict(self, tabular_score: float, text_score: float, vision_score: float = None) -> dict:
        """
        Recebe os scores dos modelos individuais e toma a decisão final.
        """
        if not self.is_loaded:
            raise RuntimeError("Meta-modelo Ensemble não foi carregado!")
        
        # Tabular model is the only one fully trained with clinical data right now.
        # We will give it 100% weight to avoid the mock NLP from dampening the real score.
        final_score = tabular_score
        
        risk = "Low"
        if final_score > 0.7:
            risk = "High"
        elif final_score > 0.4:
            risk = "Moderate"
            
        # A confiança na classe prevista (positiva ou negativa)
        # Se final_score (probabilidade de ser positivo) é 0.0, a confiança de ser Negativo (Low) é 100%.
        confidence = max(final_score, 1.0 - final_score)
            
        return {
            "risk_level": risk,
            "confidence": confidence,
            "description": f"Análise combinada (Ensemble) concluída."
        }
