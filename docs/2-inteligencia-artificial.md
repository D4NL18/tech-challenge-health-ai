# 2. Motor de Inteligência Artificial (Deep Dive)

*Read this in other languages: [English](../docs_en/2-inteligencia-artificial.md) | [Português](2-inteligencia-artificial.md)*

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
**Arquivo de Referência:** `backend/app/ml/text.py`

Perguntas fechadas não conseguem capturar nuances como "sinto uma pontada na cabeça que irradia para o pescoço quando deito". Para isso, abri um campo de "Sintomas Extras" para o paciente digitar texto livre.

*   **Modelos de Linguagem Grande (LLMs):** Para extrair significado do texto, eu envio a string para LLMs comerciais via API.
*   **Cadeia de Fallback (Alta Disponibilidade):** APIs de IA podem cair ou demorar. Implementei uma técnica chamada *Graceful Degradation* (Degradação Graciosa). O sistema tenta usar o Google Gemini 3.6; se falhar, cai para o Gemini 3.5; se a API do Google inteira estiver fora do ar, ele muda automaticamente para a OpenAI (GPT).
*   **Segurança (Prompt Injection):** Para impedir que usuários mal intencionados "hipnotizem" a IA (ex: pedindo receitas de drogas), eu izolo a instrução do sistema e o texto do usuário usando delimitadores rígidos (```).
*   **JSON Forçado:** Faço Engenharia de Prompt exigindo que a IA retorne não um texto falado, mas um objeto JSON estrito com uma pontuação de 0.0 a 1.0, para que eu possa decodificar no Python.

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

**Próximo Passo:**
Para ver como o Backend em FastAPI amarra todos esses modelos e os expõe na internet, leia [3-backend-fastapi.md](./3-backend-fastapi.md).
