# Comparativo Técnico e Clínico: Antes (Fase 1) vs. Depois (Fase 2) 🧬📊

> **Projeto:** HealthAI - Plataforma de Diagnóstico Multimodal  
> **Submódulo:** Projeto 1 - Otimização de Classificadores Clínicos via Algoritmos Genéticos e Explicabilidade  
> **Autor / Repositório:** [Tech Challenge Health AI](https://github.com/D4NL18/tech-challenge-health-ai)  

---

## 1. Contexto e Motivação da Evolução

Na **Fase 1**, a seleção de hiperparâmetros para os modelos tabulares (triagem de Câncer de Mama e Síndrome dos Ovários Policísticos - SOP) utilizava a abordagem clássica de busca por grade exaustiva (**`GridSearchCV`**) do Scikit-Learn:

```python
# Fase 1: Busca em grade discreta com métrica genérica de acurácia
grid_search = GridSearchCV(pipeline, param_grid, cv=5, scoring='accuracy', n_jobs=-1)
```

### O Problema da Fase 1 no Contexto Médico
1. **Falha Conceitual da Métrica de Acurácia:** Em triagem oncológica, um modelo com $95\%$ de acurácia global pode estar deixando escapar $10\%$ dos pacientes com câncer. Um **Falso Negativo** significa uma paciente doente liberada sem tratamento imediato, o que pode ser fatal.
2. **Espaço de Busca Rígido e Engessado:** O *GridSearch* só avaliava combinações discretas pré-definidas (ex: `n_estimators` = [50, 100, 200]). Ele era completamente cego para valores intermediários ótimos.

Na **Fase 2**, implementou-se um **Algoritmo Genético Bio-Inspirado (AG)** customizado com **Função Fitness Médica baseada no $F_2$-Score Ponderado**:

$$\text{Fitness} = F_2 = 5 \cdot \frac{\text{Precision} \cdot \text{Recall}}{4 \cdot \text{Precision} + \text{Recall}}$$

Ao dar peso quadruplicado ao **Recall (Sensibilidade)**, o AG pune severamente qualquer indivíduo que gere falsos negativos, navegando livremente pelo hiperespaço contínuo e discreto de parâmetros.

---

## 2. Matriz Comparativa: Antes vs. Depois

| Dimensão Técnica | Antes (Fase 1: GridSearch) | Depois (Fase 2: Algoritmo Genético) | Impacto Prático no Diagnóstico |
| :--- | :--- | :--- | :--- |
| **Mecanismo de Otimização** | Força bruta combinatorial estática. | Busca estocástica evolucionária com Seleção por Torneio ($k=3$), Crossover Aritmético/Uniforme e Mutação Gaussiana com bounds. | Evita mínimos locais e explora o hiperespaço com inteligência adaptativa. |
| **Métrica Orientadora** | `scoring='accuracy'` | **$F_2$-Score Clínico com 5-Fold Stratified CV** | Erradicação prioritária de Falsos Negativos. |
| **Espaço de Busca** | Rígido (apenas 12 combinações discretas por modelo). | **Contínuo e Híbrido** ($n\_estimators \in [20, 250]$, $max\_depth \in [3, 25]$ ou livre). | Descobre arquiteturas intermediárias de máxima eficiência. |
| **Elitismo e Memória** | Inexistente (avaliação estática). | **Elitismo ($E=2$)**: Preserva monotonicamente os 2 melhores indivíduos de cada geração. | Garante que o melhor hiperparâmetro nunca se perca durante a busca. |
| **Tempo de Convergência** | Rápido (~15s), mas com soluções subótimas. | Convergência no platô ótimo em ~11 min (Exp 2), com rastreamento geracional de diversidade. | Excelente custo-benefício computacional para ambiente hospitalar. |
| **Entrega ao Médico** | Probabilidade estatística crua (ex: `0.84`). | **Probabilidade + Laudo Médico Explicativo (LLM)** estruturado com fatores de risco citológicos e conduta sugerida. | Transforma números frios em decisões médicas acionáveis. |

---

## 3. Resultados Numéricos: Otimização da Random Forest (Câncer de Mama)

Comparativo direto entre o modelo entregue na Fase 1 e os 3 experimentos controlados de AG da Fase 2:

| Métrica / Configuração | Linha de Base (Fase 1) | Exp 1: Convergência Rápida | Exp 2: Exploração Balanceada (Campeão) | Exp 3: Otimização Robusta | Ganho Real (Exp 2 vs Fase 1) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Tamanho da População** | N/A (grade discreta) | 20 indivíduos | **40 indivíduos** | 80 indivíduos | - |
| **Número de Gerações** | N/A | 10 gerações | **20 gerações** | 30 gerações | - |
| **Taxa de Mutação ($p_m$)**| N/A | 0.05 | **0.15** | 0.25 | - |
| **Taxa de Crossover ($p_c$)**| N/A | 0.70 | **0.85** | 0.90 | - |
| **Recall / Sensibilidade** | 0.9048 | 0.9528 | **0.9576** | 0.9576 | **+5.8% (+528 bps)** |
| **F2-Score Clínico** | 0.9135 | 0.9527 | **0.9566** | 0.9566 | **+4.7% (+431 bps)** |
| **Acurácia Global (5 Folds)**| 0.9474 | 0.9649 | **0.9666** | 0.9666 | **+2.0% (+192 bps)** |
| **F1-Score Balanceado** | 0.9268 | 0.9530 | **0.9554** | 0.9554 | **+3.1% (+286 bps)** |
| **Área Sob a Curva (ROC-AUC)**| 0.9780 | 0.9916 | **0.9916** | 0.9916 | **+0.0136** |

### Hiperparâmetros Descobertos: Antes vs. Depois
- **Antes (Fase 1 - GridSearch):**
  `{'n_estimators': 100, 'max_depth': 10, 'criterion': 'gini'}`
- **Depois (Fase 2 - AG Campeão Exp 2):**
  `{'n_estimators': 146, 'max_depth': 18, 'min_samples_split': 4, 'min_samples_leaf': 1, 'criterion': 'entropy'}`

> **Insight Clínico:** O AG descobriu que o critério de **Entropia** (`entropy`) combinado a **146 estimadores** e profundidade **18** permite capturar nuances sutis de contorno celular e concavidade nuclear que o critério padrão Gini descartava como ruído.

---

## 4. Expansão Multimodelo da Fase 2 (Todos os Classificadores)

Além da Random Forest, a plataforma expandiu o Algoritmo Genético para toda a suíte de modelos clínicos tabulares:

### A. Resultados para Câncer de Mama
| Modelo | F2-Score Clínico | Recall (Sensibilidade) | Acurácia Global | Destaque Clínico |
| :--- | :---: | :---: | :---: | :--- |
| **Random Forest** | 0.9566 | 0.9576 | 0.9666 | Excelente robustez e baixa variância. |
| **Gradient Boosting** | 0.9596 | 0.9577 | 0.9666 | Alta separação de margens de decisão. |
| **SVM (RBF Kernel)** | **0.9698** | **0.9671** | **0.9754** | Hiperplano ótimo com dados normalizados. |
| **KNN** | 0.9300 | 0.9199 | 0.9596 | Sensibilidade a vizinhanças celulares locais. |
| **Regressão Logística**| 0.9668 | 0.9623 | 0.9719 | Alta explicabilidade dos coeficientes de risco. |
| **MLP (Rede Neural)** | **0.9717** | **0.9718** | **0.9772** | **Campeão Absoluto:** Maior sensibilidade diagnóstica. |

### B. Resultados para Síndrome dos Ovários Policísticos (PCOS)
| Modelo | F2-Score Clínico | Recall (Sensibilidade) | Acurácia Global | Destaque Clínico |
| :--- | :---: | :---: | :---: | :--- |
| **Random Forest** | 0.8235 | 0.8079 | 0.9057 | Tratamento eficaz de variáveis multimodais. |
| **Gradient Boosting** | 0.8444 | 0.8417 | 0.9020 | Boa performance com histórico hormonal. |
| **SVM** | **0.8633** | **0.8644** | 0.9094 | **Campeão Clínico:** Maior Recall para detecção de SOP. |
| **KNN** | 0.7916 | 0.7737 | 0.8890 | Agrupamento de perfis fenotípicos. |
| **Regressão Logística**| 0.8613 | 0.8590 | **0.9131** | **Maior Acurácia Global** em dados laboratoriais. |
| **MLP (Rede Neural)** | 0.8527 | 0.8594 | 0.8965 | Captura de correlações não-lineares (LH/FSH/IMC). |

---

## 5. Galeria de Gráficos e Evidências Visuais Geradas

Todos os gráficos foram gerados em alta resolução e encontram-se salvos no repositório em `backend/weights/plots/`:

### A. Benchmark Oficial da Fase 2
1. **Comparativo Consolidado dos 3 Experimentos:**  
   👉 [genetic_benchmark_comparison.png](../../backend/weights/plots/genetic_benchmark_comparison.png)
2. **Experimento 1 (Convergência Rápida):**  
   👉 [genetic_exp_1_quick.png](../../backend/weights/plots/genetic_exp_1_quick.png)
3. **Experimento 2 (Exploração Balanceada - Campeão):**  
   👉 [genetic_exp_2_balanced.png](../../backend/weights/plots/genetic_exp_2_balanced.png)
4. **Experimento 3 (Otimização Robusta):**  
   👉 [genetic_exp_3_robust.png](../../backend/weights/plots/genetic_exp_3_robust.png)

### B. Curvas de Convergência por Modelo (Câncer de Mama)
- **Random Forest:** [genetic_convergence_random_forest_cancer.png](../../backend/weights/plots/genetic_convergence_random_forest_cancer.png)
- **Gradient Boosting:** [genetic_convergence_gradient_boosting_cancer.png](../../backend/weights/plots/genetic_convergence_gradient_boosting_cancer.png)
- **SVM:** [genetic_convergence_svm_cancer.png](../../backend/weights/plots/genetic_convergence_svm_cancer.png)
- **KNN:** [genetic_convergence_knn_cancer.png](../../backend/weights/plots/genetic_convergence_knn_cancer.png)
- **Regressão Logística:** [genetic_convergence_logistic_regression_cancer.png](../../backend/weights/plots/genetic_convergence_logistic_regression_cancer.png)
- **MLP (Rede Neural):** [genetic_convergence_mlp_cancer.png](../../backend/weights/plots/genetic_convergence_mlp_cancer.png)

### C. Curvas de Convergência por Modelo (SOP / PCOS)
- **Random Forest:** [genetic_convergence_random_forest_pcos.png](../../backend/weights/plots/genetic_convergence_random_forest_pcos.png)
- **Gradient Boosting:** [genetic_convergence_gradient_boosting_pcos.png](../../backend/weights/plots/genetic_convergence_gradient_boosting_pcos.png)
- **SVM:** [genetic_convergence_svm_pcos.png](../../backend/weights/plots/genetic_convergence_svm_pcos.png)
- **KNN:** [genetic_convergence_knn_pcos.png](../../backend/weights/plots/genetic_convergence_knn_pcos.png)
- **Regressão Logística:** [genetic_convergence_logistic_regression_pcos.png](../../backend/weights/plots/genetic_convergence_logistic_regression_pcos.png)
- **MLP (Rede Neural):** [genetic_convergence_mlp_pcos.png](../../backend/weights/plots/genetic_convergence_mlp_pcos.png)

---

## 6. Como Reproduzir os Resultados

Todo o pipeline unificado pode ser executado através do script central:

```powershell
# 1. Executar o Benchmark Oficial da Fase 2 (3 Experimentos + Gráficos)
python backend/training_scripts/train_genetic_hyperopt.py --mode benchmark

# 2. Executar Otimização com Janela Gráfica Dinâmica na Tela (--live-plot)
python backend/training_scripts/train_genetic_hyperopt.py --model random_forest --disease cancer --pop 20 --gen 10 --live-plot

# 3. Executar Todos os Modelos Clínicos para Ambos os Datasets
python backend/training_scripts/train_genetic_hyperopt.py --model all --disease both --pop 30 --gen 15
```
