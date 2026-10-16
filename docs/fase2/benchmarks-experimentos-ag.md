# Benchmarks e Resultados dos Experimentos de Algoritmo Genético (Fase 2) 🧬📊

> **Módulo:** Projeto 1 - Otimização de Modelos de Diagnóstico Clínico  
> **Dataset:** Câncer de Mama (Wisconsin Diagnostic)  
> **Objetivo:** Avaliar 3 configurações do Algoritmo Genético com Validação Cruzada Estratificada (5 Folds) e função fitness $F_2$-Score (priorizando Recall/Sensibilidade diagnóstica).

---

## 1. Quadro Comparativo Consolidado

| Métrica / Configuração | Linha de Base (Fase 1) | Experimento 1 (Convergência Rápida) | Experimento 2 (Exploração Balanceada) | Experimento 3 (Otimização Robusta) |
| :--- | :---: | :---: | :---: | :---: |
| **Algoritmo Base** | Random Forest (GridSearch) | Random Forest + AG | Random Forest + AG | Random Forest + AG |
| **Tamanho da População** | N/A (grade discreta) | **20 cromossomos** | **40 cromossomos** | **80 cromossomos** |
| **Número de Gerações** | N/A | **10 gerações** | **20 gerações** | **30 gerações** |
| **Taxa de Mutação ($p_m$)** | N/A | 0.05 | 0.15 | 0.25 (adaptativa) |
| **Taxa de Crossover ($p_c$)** | N/A | 0.70 | 0.85 | 0.90 |
| **Elitismo ($E$)** | N/A | 1 melhor | 2 melhores | 2 melhores |
| **Tempo de Execução** | ~15 segundos | **188.54 segundos** | **669.67 segundos** | **1712.04 segundos** |
| **Recall / Sensibilidade** | 0.9048 | **0.9528 (+5.3%)** | **0.9576 (+5.8%)** | **0.9576 (+5.8%)** |
| **F2-Score Clínico (Fitness)** | 0.9135 | **0.9527 (+4.3%)** | **0.9566 (+4.7%)** | **0.9566 (+4.7%)** |
| **Acurácia Global (5 Folds)** | 0.9474 | **0.9649 (+1.8%)** | **0.9666 (+2.0%)** | **0.9666 (+2.0%)** |
| **F1-Score Balanceado** | 0.9268 | **0.9530 (+2.8%)** | **0.9554 (+3.1%)** | **0.9554 (+3.1%)** |
| **Área Sob a Curva (ROC-AUC)** | 0.9780 | **0.9916** | **0.9916** | **0.9916** |

---

## 2. Hiperparâmetros Ótimos Identificados pelo Algoritmo Genético

### Experimento 1 (Convergência Rápida)
```json
{
  "n_estimators": 102,
  "max_depth": null,
  "min_samples_split": 7,
  "min_samples_leaf": 1,
  "criterion": "gini"
}
```

### Experimento 2 (Exploração Balanceada - Modelo Campeão Escolhido)
```json
{
  "n_estimators": 146,
  "max_depth": 18,
  "min_samples_split": 4,
  "min_samples_leaf": 1,
  "criterion": "entropy"
}
```

### Experimento 3 (Otimização Robusta / Global)
```json
{
  "n_estimators": 182,
  "max_depth": 22,
  "min_samples_split": 3,
  "min_samples_leaf": 1,
  "criterion": "log_loss"
}
```

---

## 3. Análise Crítica dos Resultados Clínicos

1. **Impacto na Redução de Falsos Negativos:**
   - O ganho no **Recall de 90.48% para 95.76%** representa um avanço clínico substancial. Em termos práticos de triagem médica, reduziu em mais da metade a proporção de pacientes portadoras de lesões malignas que poderiam passar despercebidas pelo rastreio inicial.
2. **Eficiência da Exploração no Hiperespaço:**
   - Enquanto o GridSearch tradicional da Fase 1 avaliava apenas números redondos fixos (ex: `n_estimators`=[50, 100]), o Algoritmo Genético explorou pontos intermediários ideais de trade-off (102, 146 e 182 estimadores).
3. **Equilíbrio Custo Computacional vs. Ganho de Fitness:**
   - O Experimento 2 (40 indivíduos e 20 gerações em ~11 minutos) alcançou o mesmo platô de convergência máxima que o Experimento 3 (~28 minutos), consolidando-se como a configuração recomendada para re-treinamentos periódicos em produção hospitalar.
