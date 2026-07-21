class TextPredictor:
    def __init__(self):
        # MOCK: Aqui carregaremos o ONNX ou a pipeline Hugging Face (ClinicalBERT)
        self.model = None
        self.tokenizer = None
        self.is_loaded = False

    def load_model(self):
        print("TextPredictor: Modelo ClinicalBERT simulado carregado com sucesso.")
        self.is_loaded = True

    def predict(self, text: str) -> float:
        """
        Retorna a probabilidade baseada na inferência de PLN no texto.
        """
        if not self.is_loaded:
            raise RuntimeError("Modelo NLP não foi carregado!")
            
        # Simulação: Se houver palavras de alerta, aumenta a probabilidade
        alert_keywords = ["dor", "inchaço", "nódulo", "secreção", "anormal"]
        score = 0.2
        if any(keyword in text.lower() for keyword in alert_keywords):
            score = 0.8
            
        return score
