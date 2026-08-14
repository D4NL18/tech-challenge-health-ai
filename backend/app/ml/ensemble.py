class EnsemblePredictor:
    def __init__(self):
        # MOCK: O meta-modelo (Regressão Logística) que pega a saída dos modelos
        self.model = None
        self.is_loaded = False

    def load_model(self):
        print("EnsemblePredictor: Meta-modelo carregado com sucesso.")
        self.is_loaded = True

    def predict(self, tabular_score: float, text_score: float = None, vision_score: float = None) -> dict:
        """
        Recebe os scores dos modelos individuais e toma a decisão final combinada (Ensemble).
        """
        if not self.is_loaded:
            raise RuntimeError("Meta-modelo Ensemble não foi carregado!")
        
        # Regras do Ensemble solicitadas:
        # 1. Tudo presente: 50% Tabular, 25% Visão, 25% Texto
        # 2. Sem imagem (Tabular + Texto): 66.6% Tabular, 33.3% Texto
        # 3. Sem texto (Tabular + Imagem): 66.6% Tabular, 33.3% Visão
        # 4. Só tabular: 100% Tabular
        
        if vision_score is not None and text_score is not None:
            final_score = (tabular_score * 0.50) + (vision_score * 0.25) + (text_score * 0.25)
            weight_tabular, weight_vision, weight_text = 50, 25, 25
            desc = (f"Nossa inteligência artificial cruzou as informações fornecidas. "
                    f"Neste cálculo, os dados tabulares (laboratoriais) tiveram peso de {weight_tabular}%, "
                    f"a imagem médica {weight_vision}% e o relato de sintomas analisado pela IA generativa teve peso de {weight_text}%.")
        elif vision_score is None and text_score is not None:
            final_score = (tabular_score * 0.666) + (text_score * 0.333)
            weight_tabular, weight_text = 66.6, 33.3
            desc = (f"Nossa inteligência artificial cruzou as informações fornecidas. "
                    f"Não havendo imagem médica, os dados tabulares (laboratoriais) representaram {weight_tabular:.1f}% da decisão, "
                    f"enquanto o seu relato analisado pela IA generativa teve peso de {weight_text:.1f}%.")
        elif vision_score is not None and text_score is None:
            final_score = (tabular_score * 0.666) + (vision_score * 0.333)
            weight_tabular, weight_vision = 66.6, 33.3
            desc = (f"Nossa inteligência artificial cruzou as informações fornecidas. "
                    f"Sem relato textual detalhado, os dados tabulares representaram {weight_tabular:.1f}% da decisão, "
                    f"e a imagem médica (radiologia/biópsia) {weight_vision:.1f}%.")
        else:
            final_score = tabular_score
            desc = (f"Nossa inteligência artificial analisou seu formulário. "
                    f"Como não houve envio de imagem ou relato textual detalhado, "
                    f"o cálculo se baseou 100% nos seus dados clínicos e laboratoriais.")
        
        risk = "Low"
        if final_score > 0.7:
            risk = "High"
        elif final_score > 0.4:
            risk = "Moderate"
            
        confidence = final_score
            
        desc += " Essa combinação nos permite chegar ao risco estimado e à probabilidade apontada acima."
            
        return {
            "risk_level": risk,
            "confidence": confidence,
            "description": desc
        }
