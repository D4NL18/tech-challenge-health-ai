# Arquitetura do Backend: FastAPI

Este documento detalha a arquitetura do backend da plataforma **HealthAI**, construído utilizando o framework FastAPI em Python, focando na integração com modelos de Machine Learning de forma eficiente e escalável.

## 1. Padrão REST API
A arquitetura do backend segue o padrão RESTful. O frontend atua como cliente, enviando o payload contendo os dados clínicos (AnamnesisPayload), enquanto a API, atuando como servidor, orquestra o processamento destes dados através dos modelos de inteligência artificial e retorna o diagnóstico (DiagnosticResult) via protocolo HTTP.

## 2. Justificativa Tecnológica (FastAPI)
A adoção do FastAPI baseia-se nos seguintes pilares técnicos:
1.  **Alta Performance**: Construído sobre Starlette e Pydantic, apresenta desempenho comparável a frameworks em NodeJS e Go.
2.  **Validação de Contratos**: Integração nativa com Pydantic para validação estrita dos dados de entrada, garantindo que o payload atenda aos requisitos do modelo de IA antes do processamento.
3.  **Documentação OpenAPI**: Geração automática das especificações da API via Swagger UI, facilitando o teste e a integração entre camadas.

---

## 3. Gerenciamento de Memória (Padrão Lifespan)
Modelos de Inteligência Artificial requerem carregamento custoso em termos de I/O e processamento. Para evitar latência em tempo de execução de inferência, o sistema implementa o padrão **Lifespan** (Cold Start Management).
No ponto de entrada da aplicação (`backend/app/main.py`), o evento de inicialização (startup) é responsável por instanciar e carregar os pesos dos modelos diretamente para a memória RAM. As requisições subsequentes acessam os modelos já instanciados, garantindo inferência imediata.

---

## 4. Estrutura de Diretórios
A arquitetura de software baseia-se no padrão MVC/Service, promovendo o desacoplamento das responsabilidades de rede e regras de negócio:

```text
backend/
├── app/
│   ├── main.py
│   │   # Ponto de entrada. Gerencia o ciclo de vida (lifespan) e configuração de middlewares (CORS).
│   │
│   ├── api/routers/anamnesis.py
│   │   # Camada de Controladores. Expõe os endpoints HTTP e processa o parsing da requisição.
│   │
│   ├── models/schemas.py
│   │   # DTOs (Data Transfer Objects). Define os esquemas Pydantic para validação dos dados (In/Out).
│   │
│   ├── services/inference.py
│   │   # Camada de Serviço. Isola a lógica de negócio, orquestrando as requisições para a camada de ML.
│   │
│   └── ml/
│       # Camada de Machine Learning. Classes isoladas para inicialização e predição dos modelos preditivos.
│       ├── tabular.py             
│       ├── text.py              
│       ├── vision.py              
│       └── ensemble.py            
```

### 4.1. Fluxo de Dados (Pipeline de Inferência)
1. O payload e imagens anexadas entram via **Router** (`anamnesis.py`).
2. O **Schema** (`schemas.py`) valida a estrutura tipada.
3. Os dados validados são delegados ao **Service** (`inference.py`).
4. O **Service** distribui as features para os respectivos previsores em `ml/`.
5. As predições são consolidadas em `ml/ensemble.py`.
6. O resultado estruturado é devolvido via HTTP Response.

---

## 5. MLOps: Treinamento e Implantação

A arquitetura estabelece uma divisão clara entre os processos de treinamento (offline) e inferência (online).

### 5.1. Treinamento Local (Scripts Isolados)
O treinamento de modelos é executado isoladamente na máquina local ou em infraestrutura dedicada (e.g., máquinas virtuais com GPUs).
Para organização e versionamento, os scripts de treinamento (Jupyter Notebooks, arquivos PyTorch/Scikit-Learn) são armazenados no diretório `backend/training_scripts/`.
Estes scripts possuem caráter estritamente analítico e acadêmico, e **não** são invocados pelo contexto de execução do FastAPI.

### 5.2. Exportação de Pesos
Uma vez que as métricas alvo sejam atingidas, os modelos treinados são serializados.
*   **Modelos Tabulares (XGBoost/Random Forest)**: Exportados como `.pkl` ou `.joblib`.
*   **Modelos de Deep Learning (NLP/Visão)**: Exportados como `.onnx`, `.pt` ou `.safetensors`.

### 5.3. Implantação na API
Os pesos exportados devem ser realocados para o diretório de ativos estáticos da API, como `backend/app/weights/` (geralmente ignorados no controle de versão se excederem o limite de tamanho).

### 5.4. Atualização da Camada de Inferência
As classes mockadas na pasta `backend/app/ml/` devem ser modificadas para carregar os pesos binários e processar a inferência real.

*   **Exemplo de carregamento (`load_model`)**:
    ```python
    import pickle
    
    def load_model(self):
        with open("app/weights/modelo_tabular.pkl", "rb") as arquivo:
            self.model = pickle.load(arquivo)
        self.is_loaded = True
    ```
*   **Exemplo de predição (`predict`)**:
    ```python
    def predict(self, age, medical_history):
        dados_tratados = [[age, medical_history]] 
        probabilidade = self.model.predict_proba(dados_tratados) 
        return probabilidade
    ```

Este fluxo garante alta disponibilidade do serviço web, impedindo que tarefas assíncronas intensivas em hardware degradem a experiência da plataforma.
