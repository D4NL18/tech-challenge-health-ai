# 2. Motor de Inteligência Artificial (Deep Dive)

*Read this in other languages: [English](../docs_en/2-artificial-intelligence.md) | [Português](2-inteligencia-artificial.md)*

Neste documento, explico em detalhes como estruturei o "Cérebro" da plataforma. A medicina é complexa, e confiar em um único tipo de dado (apenas texto, ou apenas imagem) é perigoso. 

Por isso, construí um sistema **Multimodal** baseado na união de 3 pilares da Inteligência Artificial: **Machine Learning Clássico (Tabular)**, **Processamento de Linguagem Natural (Texto)** e **Visão Computacional (Imagem)**.

---

## 2.1. O Processamento Tabular (Machine Learning Clássico)
**Arquivo de Referência:** `backend/app/ml/tabular.py`

Quando o paciente preenche o formulário respondendo perguntas diretas (ex: Idade, Peso, Altura, se a dor aumenta), ele está gerando **Dados Estruturados**.

Para esse tipo de dado numérico e categórico, redes neurais profundas costumam sofrer de *Overfitting* (decorar os dados ao invés de aprender). Por isso, optei por algoritmos clássicos baseados em Árvores de Decisão, como **Random Forest** ou **XGBoost**, e também **Regressão Logística**.

*   **Vantagem:** São algoritmos extremamente leves. Eles não exigem GPU para fazer a inferência.
*   **Pipeline (Pickle):** Antes do algoritmo rodar, os dados do paciente precisam ser normalizados (ex: passar por um `StandardScaler`). Eu exporto toda essa "esteira" do treino (Pipeline) em um arquivo binário `.pkl` usando a biblioteca `pickle` ou `joblib`, e o FastAPI apenas o carrega na RAM e executa.
*   **Predict Proba:** Em vez de pedir pro modelo dizer se o paciente está "Doente" ou "Saudável", eu uso a função `predict_proba()`. Ela me devolve uma **porcentagem matemática** de confiança (ex: 82% de chance), essencial para o meu sistema de votação final.

---

## 2.2. O Processamento de Texto (Processamento de Linguagem Natural - NLP)
**Arquivos de Referência:** `backend/app/ml/text.py`, `backend/knowledge_base/query_rag.py` e `backend/app/services/llm_governance.py`

Perguntas fechadas não conseguem capturar nuances como "sinto uma pontada na cabeça que irradia para o pescoço quando deito". Para isso, já na Fase 1 foi adiantado um campo de "Sintomas Extras" com RAG em ChromaDB (`all-MiniLM-L6-v2`), que foi aprimorado na Fase 2 com governança avançada de LLMs:

*   **Prompts em Inglês com Saída em Português (Tokenomics):** Os prompts de sistema (`SYSTEM_PROMPT`) são redigidos em inglês técnico conciso (economizando ~25-30% de tokens no tokenizador BPE/SentencePiece e elevando a aderência às instruções), mas exigem que toda resposta ou justificativa final seja gerada em **Português do Brasil (`pt-BR`)**.
*   **Cadeia de Fallback Multi-Nível e Cross-Provider (Alta Disponibilidade):** O sistema tenta usar o **Google Gemini 2.5 Flash**; se falhar, cai para o **Gemini 2.0 Flash**; se a API do Google inteira estiver indisponível, alterna automaticamente para a **OpenAI (`gpt-4o-mini`)** (ou na ordem inversa caso o admin priorize GPT), e possui degradação graciosa / fallback heurístico offline.
*   **Segurança Restrita contra Prompt Injection (`PromptSecurityGuard`):** Separa estritamente `system_instruction` (`role="system"`) do input do usuário (`role="user"`), impõe limite rígido de caracteres, neutraliza delimitadores, confina o input em tags XML `<untrusted_user_input>` e bloqueia de forma determinística via Regex (PT/EN) tentativas de *Prompt Injection* e *Jailbreak* antes mesmo de chamar a API.
*   **Cache em Duas Camadas para Textos Similares (`SimilarityLLMCache`):** Combina cache L1 (Hash SHA-256 sobre texto normalizado sem acentos/pontuação) e cache L2 (Similaridade de Cosseno $\ge 0.85$ sobre 3-gramas de caracteres e palavras), retornando respostas em $< 1\text{ ms}$ a custo zero de tokens para relatos clínicos ou perguntas similares.
*   **JSON Forçado:** Exige retorno estrito em JSON (`response_mime_type="application/json"` / `json_object`) com `temperature=0.0`.

---

## 2.3. O Processamento de Imagens (Visão Computacional)
**Arquivo de Referência:** `backend/app/ml/vision.py`

Para diagnósticos que dependem de raio-x, ressonâncias ou fotos (ex: Câncer de Mama ou Melanoma), implementei Redes Neurais Convolucionais (CNNs) usando **PyTorch**.

*   **Modelos Base:** Utilizo arquiteturas famosas focadas em alta precisão e baixo peso (como ResNet, DenseNet ou EfficientNet).
*   **Pré-Processamento Vital:** Máquinas de Raio-X diferentes geram imagens de cores e contrastes diferentes. Antes de mandar para a IA, aplico duas técnicas no Python usando OpenCV (`cv2`):
    1.  **CLAHE:** Normaliza o contraste da imagem para evidenciar veias e nódulos escondidos.
    2.  **Auto-Crop:** Encontra as bordas do seio/tumor e corta todo o fundo preto "morto", garantindo que a IA foque apenas no tecido relevante.
*   **Tensores:** A imagem é convertida de matriz de pixels para Tensores Matemáticos normalizados antes da inferência final.

---

## 2.4. A Decisão Final: Ensemble (Weighted Soft Voting)
**Arquivo de Referência:** `backend/app/ml/ensemble.py`

Com os 3 especialistas tendo dado sua nota de confiança (ex: Tabular = 80%, Texto = 90%, Visão = 60%), eu preciso de uma decisão final.

Uso um padrão de **Ensemble** focado em **Weighted Soft Voting** (Votação Suave Ponderada).

Eu faço a média matemática das 3 pontuações, mas dou "pesos" diferentes dependendo da confiabilidade da fonte. 
*   Exemplo para Câncer: Os dados numéricos de laboratório costumam ser o pilar da verdade. Eu dou **50% de peso** para o Tabular, **25%** para o Raio-X e **25%** para o Relato do paciente.
*   Se o paciente não enviar a Imagem (ou a API de Texto falhar), o sistema recalcula os pesos distribuindo a carga entre os modelos sobreviventes.

No fim, o Ensemble me devolve uma nota de 0 a 100%, que é formatada e enviada para o Frontend exibir ao médico!

---

## 2.5. Fase 2: Otimização de Hiperparâmetros via Algoritmos Genéticos (Projeto 1)
**Arquivo de Referência:** `backend/app/genetic/hyperopt/`
*   **Codificação Cromossômica Híbrida:** Cromossomos representam genes inteiros (`n_estimators`, `max_depth`), reais com escala logarítmica (`C`, `gamma`) e categóricos (`criterion`).
*   **Função Fitness Clínica ($F_2$-Score):** Dá peso 4 vezes maior ao **Recall** (Sensibilidade) do que à Precisão, forçando o algoritmo a priorizar a minimização de Falsos Negativos (fundamental em oncologia).
*   **Operadores:** Seleção por Torneio ($k=3$), Crossover Uniforme/Aritmético e Mutação Gaussiana com bounds rígidos e Elitismo de 2 melhores.
*   **Resultados:** Recall elevado de 90.48% (Baseline Fase 1) para **95.76%** (Melhor modelo sintonizado por AG na Fase 2).

---

## 2.6. Fase 2: Roteamento Hospitalar (VRP) com Algoritmos Genéticos (Projeto 2)
**Arquivo de Referência:** `backend/app/genetic/routing/`
*   **Problema Modelado:** Roteamento de Veículos com Capacidade e Prioridades (CVRP/VRPTW).
*   **Cromossomo de Permutação e Crossover OX (Order Crossover):** Garante rotas livres de duplicidades de paradas.
*   **Mutação 2-opt Inversion:** Inverte subtrechos de rota desfazendo cruzamentos viários ineficientes.
*   **Restrições Médicas no Fitness:**
    1. *Urgência de Medicamentos Críticos:* Paradas prioritárias (vacinas, bolsas de sangue) são sequenciadas nas primeiras etapas.
    2. *Capacidade de Carga Térmica:* Penaliza sobrecarga em kg nos veículos.
    3. *Autonomia:* Respeita o raio máximo de km por veículo.

---

## 2.7. Explicabilidade Clínica e Assistente Logístico com LLMs
**Arquivos de Referência:** `backend/app/services/clinical_llm.py` e `backend/app/services/logistics_llm.py`
*   **Laudos Médicos:** A LLM (Google Gemini Flash / OpenAI) recebe os percentis laboratoriais do paciente e converte o score numérico em um laudo estruturado com fatores de risco, justificativa e condutas sugeridas.
*   **Roteiros Operacionais e Relatórios:** A LLM gera o itinerário passo a passo para o motorista (alertando sobre controle térmico 2°C a 8°C) e relatórios executivos de eficiência com estimativa de tempo e combustível economizados.

---

**Próximo Passo:**
Para ver como o Backend em FastAPI amarra todos esses modelos e os expõe na internet, leia [3-backend-fastapi.md](./3-backend-fastapi.md).

