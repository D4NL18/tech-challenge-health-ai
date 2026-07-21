class TabularPredictor:
    def __init__(self):
        # MOCK: Aqui no futuro faremos: self.model = pickle.load(open("model.pkl", "rb"))
        self.model = None
        self.is_loaded = False

    def load_model(self):
        print("TabularPredictor: Modelo XGBoost/RF simulado carregado com sucesso.")
        self.is_loaded = True

    def predict(self, age: int, medical_history: str) -> float:
        """
        Retorna a probabilidade baseada nos dados tabulares estruturados.
        """
        if not self.is_loaded:
            raise RuntimeError("Modelo Tabular não foi carregado!")
            
        # Simulação: maior a idade, leve aumento na probabilidade
        base_prob = 0.1
        if age > 50:
            base_prob += 0.3
        
        return min(base_prob, 1.0)
