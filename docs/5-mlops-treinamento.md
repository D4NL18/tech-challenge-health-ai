# 5. MLOps e Treinamento de Modelos

*Read this in other languages: [English](../docs_en/5-mlops-training.md) | [Português](5-mlops-treinamento.md)*

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

## 5.4. Calibração Hiperparamétrica por Algoritmos Genéticos (Fase 2)
**Arquivo de Referência:** `backend/training_scripts/train_genetic_hyperopt.py`

Na Fase 2, substituímos o GridSearch tradicional (que testa parâmetros em grade rígida e cara) por um **Algoritmo Genético Bio-Inspirado** (`app/genetic/hyperopt/optimizer.py`), oferecendo dois modos de operação via CLI:

1. **Modo Benchmark (`--mode benchmark`):**
   Executa a bateria clássica dos 3 experimentos exigidos pelo desafio (Quick, Balanced, Robust), compara com o Baseline da Fase 1, gera gráficos de convergência e exporta o relatório `backend/weights/genetic_experiments_results.json` para consumo direto pelo Painel Administrativo.
   ```bash
   python training_scripts/train_genetic_hyperopt.py --mode benchmark
   ```

2. **Modo Multimodelo Clínico (`--mode multimodel`):**
   Permite otimização hiperparamétrica em 6 famílias de modelos tabulares (`random_forest`, `gradient_boosting`, `svm`, `knn`, `logistic_regression`, `mlp`) em ambos os datasets clínicos (`cancer`, `pcos` ou `both`), com acompanhamento visual em tempo real (`--live-plot`).
   ```bash
   python training_scripts/train_genetic_hyperopt.py --mode multimodel --model all --disease both --pop 30 --gen 15 --live-plot
   ```

- **Cromossomo Híbrido Multitipo:** Codifica genes inteiros (`int`, ex: `n_estimators`), inteiros opcionais (`int_or_none`, ex: `max_depth`), contínuos (`float`), contínuos em escala logarítmica de base 10 (`float_log`, ex: `C`, $\gamma$, `learning_rate` entre $10^{-4}$ e $10^{2}$) e categóricos (`cat`, ex: `criterion`, `class_weight`).
- **Operadores Genéticos:** Seleção por Torneio ($k=3$) ou Roleta com Elitismo estrito ($E=2$), Crossover Híbrido (Aritmético Ponderado para genes contínuos e Uniforme para discretos/categóricos) e Mutação Gaussiana com reflexão nos limites e perturbação no expoente logarítmico.
- **Validação Cruzada Segura:** K-Fold Stratified ($k=5$) em cada indivíduo da população dentro de um `Pipeline` com `StandardScaler`, eliminando qualquer risco de Data Leakage entre treino e validação.

---

## 5.5. Função Fitness Clínica ($F_2$-Score)
Em diagnósticos médicos (Câncer de Mama e SOP), um **Falso Negativo** (não diagnosticar um paciente doente) é imensamente mais prejudicial que um Falso Positivo.
Por isso, a função fitness foi desenhada como:

$$\text{Fitness} = 0.70 \times F_2 + 0.20 \times \text{Recall} + 0.10 \times \text{Accuracy} - \text{Penalidade de Complexidade}$$

Onde $F_2$-score confere peso dobrado à revocação ($Recall$) sobre a precisão ($Precision$).

---

## 5.6. Resultados dos 3 Experimentos Sistemáticos
Executamos 3 experimentos com variações estruturadas de população, gerações e mutação:

| Métrica | Baseline (Fase 1 GridSearch) | Exp 1 (Exploratório) | Exp 2 (Equilibrado) | Exp 3 (Convergência) |
| :--- | :--- | :--- | :--- | :--- |
| **População / Gerações** | Grade Fixa | 20 / 10 | 40 / 20 | 80 / 30 |
| **$F_2$-Score** | 0.9135 | 0.9527 | **0.9566 (+4.7%)** | 0.9566 |
| **Recall (Maligno)** | 0.9048 | 0.9528 | **0.9576 (+5.8%)** | 0.9576 |
| **Acurácia** | 0.9386 | 0.9631 | **0.9666 (+3.0%)** | 0.9666 |
| **Tempo de Execução** | ~18s | 8.2s | 30.7s | 99.4s |

O modelo vencedor do Experimento 2 foi serializado em `backend/weights/modelo_random_forest_cancer_genetic.pkl` e as estatísticas detalhadas gravadas em `backend/weights/genetic_experiments_results.json`.

---

**Próximo Passo:**
Pronto para testar o sistema? Acesse o último módulo para pegar dados de teste criados sinteticamente para você em [6-exemplos-testes.md](./6-exemplos-testes.md).
