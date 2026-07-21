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
        
        # Simulação: Faz a média dos scores providos
        scores = [tabular_score, text_score]
        if vision_score is not None:
            scores.append(vision_score)
            
        final_score = sum(scores) / len(scores)
        
        risk = "Low"
        if final_score > 0.7:
            risk = "High"
        elif final_score > 0.4:
            risk = "Moderate"
            
        return {
            "risk_level": risk,
            "confidence": final_score,
            "description": f"Análise combinada (Ensemble) concluída."
        }
