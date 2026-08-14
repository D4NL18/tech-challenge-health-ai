# 5. MLOps e Treinamento de Modelos

*Read this in other languages: [English](../docs_en/5-mlops-treinamento.md) | [Português](5-mlops-treinamento.md)*

Este documento detalha o ciclo de vida dos modelos de Machine Learning neste projeto. Ele responde à pergunta: *"Como um modelo sai de um experimento de dados para um produto de software rodando na internet?"*

Como estou lidando com os papéis tanto de **Cientista de Dados** quanto de **Engenheiro de Software**, decidi separar essas responsabilidades fisicamente no projeto para evitar que as coisas se misturem.

---

## 5.1. A Separação: `training_scripts/` vs `app/ml/`

Se você olhar a estrutura de pastas do Backend, vai notar que o aprendizado de máquina existe em dois lugares diferentes. Isso é intencional.

1.  **Pasta `training_scripts/` (O Laboratório):** 
    *   Aqui é onde eu atuo como Cientista de Dados.
    *   É o ambiente "Offline". Estes arquivos só rodam no meu computador local (ou em um Jupyter Notebook no Google Colab/Kaggle com GPUs potentes).
    *   Eles limpam os arquivos CSV bagunçados (Data Cleaning), testam milhares de parâmetros diferentes (*Grid Search*) e gastam horas treinando a Inteligência Artificial.
    *   *Importante:* A API do FastAPI **nunca** olha para essa pasta. Ela não existe no servidor de produção.

2.  **Pasta `app/ml/` (A Fábrica):**
    *   Aqui é onde atuo como Engenheiro de Software.
    *   Nesta pasta, o modelo de IA já não "aprende" mais nada. O cérebro matemático já está pronto e "congelado".
    *   Os arquivos aqui apenas sabem como pegar um modelo pronto, injetar os dados do paciente, e tirar uma probabilidade.
    *   Este é o ambiente "Online" que roda no Cloud Run.

---

## 5.2. Serialização e Exportação (Criando os "Pesos")
Quando o treinamento lá no `training_scripts/` termina e a IA atinge uma acurácia alta (ex: 95%), eu preciso "salvar" o cérebro dela para enviar pro `app/ml/`.

A esse processo damos o nome de **Serialização**. 
Os modelos treinados se tornam arquivos grandes que chamamos informalmente de "Pesos".

1.  **Modelos Tabulares (Random Forest, XGBoost):** 
    Salvo a pipeline inteira num arquivo binário usando `pickle` ou `joblib` (ex: `modelo_pcos.pkl`). Ele contém tanto as regras lógicas quanto a esteira de pré-processamento.
2.  **Modelos de Deep Learning (PyTorch):** 
    Salvo o Dicionário de Estados (State Dictionary) contendo as matrizes matemáticas dos neurônios em um arquivo `.pth` (ex: `modelo_resnet_cancer.pth`).

---

## 5.3. A Ponte: Pasta `weights/`
Para colocar o modelo no servidor da internet, eu pego o arquivo `.pkl` ou `.pth` gerado localmente e copio para a pasta `backend/app/weights/`. 

Quando o FastAPI inicializa no Cloud Run, é dessa pasta que ele lê os modelos para jogar na RAM, conectando assim o mundo da Ciência de Dados com a Engenharia de Software Backend.

*(Aviso: Como arquivos de pesos de redes neurais pesam gigabytes, geralmente eles são ignorados no `.gitignore` e você precisa baixá-los do Google Drive ou Google Cloud Storage para rodar o projeto localmente).*

---

**Próximo Passo:**
Pronto para testar o sistema? Acesse o último módulo para pegar dados de teste criados sinteticamente para você em [6-exemplos-testes.md](./6-exemplos-testes.md).
