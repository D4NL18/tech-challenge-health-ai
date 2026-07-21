# Arquitetura do Sistema: Plataforma de Anamnese e Diagnóstico Virtual
**Foco da Arquitetura: Implementação de Baixíssimo Custo no Google Cloud Platform (GCP)**

Para contornar o alto custo de instâncias gerenciadas como o Cloud SQL e o GKE (Kubernetes), esta arquitetura foi redesenhada utilizando serviços *Serverless* (que escalam a zero, ou seja, você só paga se houver requisições) e recursos do **Free Tier (Nível Gratuito)** do Google Cloud.

---

## 1. Visão Geral da Infraestrutura (GCP Low-Cost)

* **Frontend (Angular):** Firebase Hosting (Nível gratuito generoso, CDN global embutida).
* **Backend Core (Java Spring Boot):** Google Cloud Run (Serverless, escala a zero, 2 milhões de requisições gratuitas/mês).
* **AI Engine (Python FastAPI):** Google Cloud Run (Serverless, alocação de CPU/RAM apenas durante a inferência).
* **Banco de Dados (Relacional):** PostgreSQL rodando em uma máquina virtual (VM) **Compute Engine `e2-micro`** (Faz parte do *Always Free* tier do GCP, custo virtualmente zero).
* **Armazenamento de Imagens:** Google Cloud Storage - GCS (5 GB de armazenamento gratuito por mês).

---

## 2. Detalhamento dos Componentes Core

### 2.1. Frontend (Angular via Firebase Hosting)
Como o Angular gera arquivos estáticos (HTML, CSS, JS), não faz sentido pagar por um servidor para hospedá-lo.
* **Hospedagem:** Fazer o build da aplicação (`ng build`) e realizar o deploy no **Firebase Hosting** (integrado nativamente ao GCP). O Firebase oferece SSL gratuito, domínio customizado e CDN rápida a custo zero para tráfego inicial.
* **Funcionalidades:** Coleta dinâmica de anamnese e upload direto de imagens para o backend.

### 2.2. Banco de Dados de Baixo Custo (A Alternativa ao Cloud SQL)
O Cloud SQL cobra uma taxa fixa mensal alta apenas para manter a instância ligada. A solução de menor custo no GCP é a abordagem "Faça Você Mesmo" (IaaS):
* **Compute Engine (e2-micro):** O GCP oferece 1 instância `e2-micro` gratuita por mês (na região us-central1, us-east1 ou us-west1) e 30 GB de disco Standard grátis.
* **Implementação:** Você cria essa maquininha, instala o Docker e sobe um container do **PostgreSQL**.
* **Trade-off:** Você não terá backups automáticos diários (terá que criar um script simples via *cron* que faz o dump e joga para o Cloud Storage) nem alta disponibilidade, mas o custo será **$0.00**.

### 2.3. Backend Core (Java Spring Boot via Cloud Run)
* **Containerização:** O Spring Boot será empacotado em uma imagem Docker. Para economizar RAM e tempo de inicialização (Cold Start), recomenda-se compilar o Java nativamente usando **GraalVM / Spring Native**.
* **Deploy:** Hospedado no **Cloud Run**.
* **Fluxo:** Recebe a requisição, salva os dados na VM do Postgres (`e2-micro`), faz o upload da imagem médica para o bucket do **Google Cloud Storage (GCS)** e faz uma requisição HTTP interna para o Microsserviço de IA.

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
O FastAPI pega a saída dos 3 modelos (Tabular, BERT, MobileNet) e passa por uma Regressão Logística leve que toma a decisão final (ex: "78% de chance de patologia X") e devolve o JSON para o Spring Boot.

---

## 4. Etapas de Desenvolvimento e MLOps "Low-Cost"

Para evitar os custos do Vertex AI Pipeline, o fluxo de MLOps usará ferramentas gratuitas.

### Etapa 1: Treinamento "Free" (Google Colab / Kaggle)
* Não treine modelos no GCP. Utilize o **Google Colab (Free tier)** que oferece acesso a GPUs (T4) temporárias gratuitas.
* Lá, você fará o aumento de dados (Data Augmentation) com as GANs e treinará o BERT e a CNN.
* Ao final do treinamento, o script no Colab exporta os pesos (`.safetensors`, `.onnx` e `.pkl`) e faz o upload diretamente para um bucket gratuito do **Google Cloud Storage (GCS)**.

### Etapa 2: Construção da API (FastAPI) e Lifespan
* **Inicialização Inteligente:** Quando o Cloud Run iniciar a API Python, ela usa o bloco `lifespan` do FastAPI para fazer o download dos modelos do bucket do GCS e carregá-los na RAM **uma única vez**.
* Isso economiza custos de chamadas a serviços externos e minimiza a latência.

### Etapa 3: Deploy Contínuo (CI/CD) com GitHub Actions
* Em vez de pagar pelo Cloud Build, utilize o **GitHub Actions** (gratuito para repositórios públicos e com cota para privados).
* Quando você fizer um push de código, o GitHub Actions faz o build da imagem Docker do Spring Boot e do FastAPI, e sobe as imagens para o **Artifact Registry** no GCP, executando em seguida a atualização do Cloud Run.

### Etapa 4: Monitoramento "Zero Cost"
* O feedback dos médicos (validação dos laudos gerados pela IA) ficará salvo no seu PostgreSQL (`e2-micro`).
* Periodicamente (ex: a cada 3 meses), você extrai esses dados novos, joga no Google Colab novamente, retreina a IA para corrigir *Data Drift*, e sobrepõe os arquivos de modelo no Bucket do GCS. O Cloud Run assumirá a versão mais inteligente no próximo restart.