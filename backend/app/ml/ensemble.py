"""
==================================================================================================
ARQUIVO: ml/ensemble.py (META-MODELO DE ENSEMBLE LEARNING)
==================================================================================================
Objetivo:
Em Machine Learning Avançado, raramente confiamos a vida de um paciente a um único algoritmo.
O "Ensemble" (Conjunto) é a técnica de pegar as predições (probabilidades) de vários modelos
independentes (Ex: Modelo de Imagem, Modelo de Texto, Modelo Tabular) e combiná-las para
tomar uma decisão final mais precisa, imitando uma junta médica onde vários especialistas votam.

Arquitetura (Hard Voting / Soft Voting):
Nesta implementação específica, estou usando um "Weighted Soft Voting" (Votação Suave Ponderada),
onde faço a média matemática das probabilidades individuais, mas dou "pesos" diferentes para cada
especialista baseado no quão confiável aquele tipo de dado costuma ser.
==================================================================================================
"""

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
        ----------------------------------------------------------------------------------------------
        FUNÇÃO: predict (Meta-Predição)
        Objetivo: Receber a nota de 0 a 1 de cada modelo individual e fundi-las.
        
        Detalhe Técnico (Degradação Graciosa):
        Sistemas robustos não devem falhar ("quebrar a tela") se um componente cair.
        Se a API do Gemini falhar (ou o usuário não digitar texto) o text_score chega como 'None'.
        Se não houver upload de imagem, o vision_score é 'None'.
        Em vez de gerar um erro, o Ensemble recalcula os pesos matematicamente ignorando o modelo
        faltante, focando apenas nos modelos que tiveram sucesso (Degradação Graciosa).
        ----------------------------------------------------------------------------------------------
        """
        if not self.is_loaded:
            raise RuntimeError("Meta-modelo Ensemble não foi carregado!")
        
        # Regras de Ponderação Matemáticas:
        # Se tenho as 3 fontes de dados ativas: Tabular leva 50%, Imagem e Texto dividem o restante.
        if vision_score is not None and text_score is not None:
            final_score = (tabular_score * 0.50) + (vision_score * 0.25) + (text_score * 0.25)
            weight_tabular, weight_vision, weight_text = 50, 25, 25
            desc = (f"Nossa inteligência artificial cruzou as informações fornecidas. "
                    f"Neste cálculo, os dados tabulares (laboratoriais) tiveram peso de {weight_tabular}%, "
                    f"a imagem médica {weight_vision}% e o relato de sintomas analisado pela IA generativa teve peso de {weight_text}%.")
                    
        # Se a Imagem Falta/Falha: Distribuo 2/3 da força para Tabular e 1/3 para NLP (Texto)
        elif vision_score is None and text_score is not None:
            final_score = (tabular_score * 0.666) + (text_score * 0.333)
            weight_tabular, weight_text = 66.6, 33.3
            desc = (f"Nossa inteligência artificial cruzou as informações fornecidas. "
                    f"Não havendo imagem médica, os dados tabulares (laboratoriais) representaram {weight_tabular:.1f}% da decisão, "
                    f"enquanto o seu relato analisado pela IA generativa teve peso de {weight_text:.1f}%.")
                    
        # Se o Texto Falta/Falha: Distribuo 2/3 para Tabular e 1/3 para Imagem
        elif vision_score is not None and text_score is None:
            final_score = (tabular_score * 0.666) + (vision_score * 0.333)
            weight_tabular, weight_vision = 66.6, 33.3
            desc = (f"Nossa inteligência artificial cruzou as informações fornecidas. "
                    f"Sem relato textual detalhado, os dados tabulares representaram {weight_tabular:.1f}% da decisão, "
                    f"e a imagem médica (radiologia/biópsia) {weight_vision:.1f}%.")
                    
        # Fallback Extremo: Só há dados numéricos preenchidos
        else:
            final_score = tabular_score
            desc = (f"Nossa inteligência artificial analisou seu formulário. "
                    f"Como não houve envio de imagem ou relato textual detalhado, "
                    f"o cálculo se baseou 100% nos seus dados clínicos e laboratoriais.")
        
        # Limiares Clássicos de Decisão Clínica (Thresholds)
        # Convertendo o percentual final contínuo em uma classificação de risco categórica
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
