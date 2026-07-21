# Arquitetura do Sistema: Plataforma de Anamnese e Diagnóstico Virtual
**Foco da Arquitetura: Implementação de Baixíssimo Custo no Google Cloud Platform (GCP)**

Para contornar o alto custo de instâncias gerenciadas como o Cloud SQL e o GKE (Kubernetes), esta arquitetura foi redesenhada utilizando serviços *Serverless* (que escalam a zero, ou seja, você só paga se houver requisições) e recursos do **Free Tier (Nível Gratuito)** do Google Cloud.

---

## 1. Visão Geral da Infraestrutura (GCP Low-Cost)

* **Frontend (Angular):** Firebase Hosting (Nível gratuito generoso, CDN global embutida).
* **Backend / AI Engine (Python FastAPI):** Google Cloud Run (Serverless, alocação de CPU/RAM apenas durante a inferência).
* **Armazenamento de Imagens (Opcional/Temporário):** Google Cloud Storage - GCS (5 GB de armazenamento gratuito por mês).

---

## 2. Detalhamento dos Componentes Core

### 2.1. Frontend (Angular via Firebase Hosting)
Como o Angular gera arquivos estáticos (HTML, CSS, JS), não faz sentido pagar por um servidor para hospedá-lo.
* **Hospedagem:** Fazer o build da aplicação (`ng build`) e realizar o deploy no **Firebase Hosting** (integrado nativamente ao GCP). O Firebase oferece SSL gratuito, domínio customizado e CDN rápida a custo zero para tráfego inicial.
* **Funcionalidades:** Coleta dinâmica de anamnese e upload direto de imagens para o backend.

### 2.2. Backend Stateless (Python FastAPI via Cloud Run)
* **Arquitetura Stateless:** O sistema não salva histórico de pacientes ou diagnósticos no longo prazo. O processamento ocorre totalmente em memória para reduzir custos operacionais e simplificar a infraestrutura.
* **Deploy:** Hospedado no **Cloud Run**.
* **Fluxo:** Recebe a requisição diretamente do Angular (podendo receber a imagem no formato Multipart), faz a inferência utilizando os modelos de IA carregados na RAM, e devolve o laudo imediatamente para o frontend.

---

## 3. Deep Dive: Motor de Inteligência Artificial (Python FastAPI)

Para economizar e manter a eficiência, a IA não rodará em GPUs caras no GCP, mas sim na CPU do Cloud Run com os modelos otimizados.

### 3.1. Processamento de Dados Tabulares (Perguntas Fechadas)
* **Modelo:** **XGBoost** ou **Random Forest** (Scikit-Learn).
* **Vantagem de Custo:** Extremamente leves para treinar e rodar. Consomem pouquíssima RAM no Cloud Run. Retornam a probabilidade baseada no histórico médico e idade.

### 3.2. Processamento de Texto Livre (Relatos de Sintomas)
* **Modelo:** Ao invés de usar APIs pagas (como OpenAI) ou rodar LLMs gigantes (como Llama 3 que exige GPU), utilizaremos o **ClinicalBERT** ou **BERTimbau** (Hugging Face).
* **Otimização para CPU:** O modelo será convertido para o formato **ONNX** ou quantizado (Int8). Isso reduz o tamanho do modelo de 500MB para ~100MB e permite inferência incrivelmente rápida em CPU comum no Cloud Run, barateando a operação.

### 3.3. Processamento de Imagens (Visão Computacional)
* **Modelo:** Uma Rede Neural Convolucional (CNN) como **EfficientNetB0** ou **MobileNetV2** (PyTorch/TensorFlow). Estas arquiteturas foram desenhadas especificamente para inferência rápida e barata com alta acurácia.
* **Ação offline das GANs:** As Redes Adversariais (GANs) usadas para gerar exames falsos e melhorar o dataset **nunca** rodarão no GCP. Elas serão executadas apenas no momento de treinamento offline para gerar dados.

### 3.4. Camada de Ensemble (Fusão Tardia)
O FastAPI pega a saída dos 3 modelos (Tabular, BERT, MobileNet) e passa por uma Regressão Logística leve que toma a decisão final (ex: "78% de chance de patologia X") e devolve o JSON diretamente para o Angular no Frontend.

---

## 4. Etapas de Desenvolvimento e MLOps "Low-Cost"

Para evitar os custos do Vertex AI Pipeline, o fluxo de MLOps usará ferramentas gratuitas.

### Etapa 1: Treinamento Local e Armazenamento (Histórico)
* O treinamento será realizado localmente na máquina do desenvolvedor (via Python/Jupyter Notebooks).
* Para manter o histórico acadêmico e de estudos, os scripts e notebooks de treinamento ficarão versionados dentro do repositório, especificamente na pasta `backend/training_scripts/`.
* É fundamental ressaltar que os scripts dessa pasta **não interferem** na operação da API FastAPI.
* Após o treinamento local, os pesos (`.pkl`, `.onnx`) são gerados e salvos em uma pasta de pesos (`backend/app/weights/`) para serem consumidos pela API.

### Etapa 2: Construção da API (FastAPI) e Lifespan
* **Inicialização Inteligente:** Quando o Cloud Run ou a API local iniciar, ela usará o bloco `lifespan` do FastAPI para carregar os pesos salvos em `app/weights/` para a RAM **uma única vez**.
* Isso economiza custos de chamadas a serviços externos e minimiza a latência.

### Etapa 3: Deploy Contínuo (CI/CD) com GitHub Actions
* Em vez de pagar pelo Cloud Build, utilize o **GitHub Actions** (gratuito para repositórios públicos e com cota para privados).
* Quando você fizer um push de código, o GitHub Actions faz o build da imagem Docker do FastAPI e sobe a imagem para o **Artifact Registry** no GCP, executando em seguida a atualização do Cloud Run.

### Etapa 4: Coleta de Dados para Retreinamento (Opcional)
* Como a arquitetura agora é totalmente stateless e focada na privacidade por padrão (sem PostgreSQL), não há retenção de histórico.
* Caso haja interesse futuro em MLOps (retreinamento por Data Drift), será necessário implementar um mecanismo opt-in leve e isolado para coleta de métricas, mas atualmente os modelos são estáticos.