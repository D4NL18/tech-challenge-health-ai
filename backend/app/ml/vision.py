class VisionPredictor:
    def __init__(self):
        # MOCK: Aqui carregaremos o ONNX / TensorFlow Lite / PyTorch MobileNet
        self.model = None
        self.is_loaded = False

    def load_model(self):
        print("VisionPredictor: Modelo CNN (MobileNet) simulado carregado com sucesso.")
        self.is_loaded = True

    def predict(self, image_bytes: bytes) -> float:
        """
        Recebe a imagem em bytes e retorna a probabilidade baseada na visão computacional.
        """
        if not self.is_loaded:
            raise RuntimeError("Modelo de Visão não foi carregado!")
            
        # Simulação: Retorna uma probabilidade fixa apenas para fins de teste
        return 0.65
