# 2. Artificial Intelligence Engine (Deep Dive)

*Read this in other languages: [English](2-artificial-intelligence.md) | [Português](../docs/2-inteligencia-artificial.md)*

In this document, I explain in detail how I structured the "Brain" of the platform. Medicine is complex, and relying on a single type of data (only text, or only image) is dangerous.

Therefore, I built a **Multimodal** system based on the union of 3 pillars of Artificial Intelligence: **Classic Machine Learning (Tabular)**, **Natural Language Processing (Text)**, and **Computer Vision (Image)**. In Phase 2, this was further extended with **Bio-Inspired Genetic Algorithms** and **LLM Clinical Governance**.

---

## 2.1. Tabular Processing (Classic Machine Learning)
**Reference File:** `backend/app/ml/tabular.py`

When the patient fills out the form answering direct questions (e.g., Age, Weight, Height, whether pain increases under palpation), they are generating **Structured Data**.

For this type of numerical and categorical data, deep neural networks often suffer from *Overfitting* (memorizing the data instead of learning). Therefore, I opted for classic algorithms based on Decision Trees, such as **Random Forest** or **XGBoost**, as well as **Logistic Regression**.

*   **Advantage:** They are extremely lightweight algorithms. They do not require a GPU to perform inference.
*   **Pipeline (Pickle):** Before the algorithm runs, the patient's data needs to be normalized (e.g., go through a `StandardScaler`). I export this entire training "conveyor belt" (Pipeline) into a binary `.pkl` file using the `pickle` or `joblib` library, and FastAPI loads it into RAM and executes it.
*   **Predict Proba:** Instead of asking the model to just say if the patient is "Sick" or "Healthy", I use the `predict_proba()` function. It returns a **mathematical percentage** of confidence (e.g., 82% chance), essential for my final voting system.

---

## 2.2. Text Processing (Natural Language Processing - NLP)
**Reference File:** `backend/app/ml/text.py`

Closed-ended questions cannot capture nuances like "I feel a sharp pain in my head that radiates to my neck when I lie down". For this, I opened an "Extra Symptoms" field for the patient to type free text.

*   **Large Language Models (LLMs):** To extract meaning from the text, I send the string to commercial LLMs via API.
*   **Fallback Chain (High Availability):** AI APIs can go down or be slow. I implemented a technique called *Graceful Degradation*. The system tries to use Google Gemini 1.5 Flash; if it fails, it falls back to OpenAI GPT-4o-mini; if external APIs are unreachable, it falls back to a deterministic clinical heuristic engine.
*   **Security (Prompt Injection):** To prevent malicious users from "hypnotizing" the AI (e.g., asking for unauthorized prescriptions), I use active prompt security filtering isolating the system instruction from user input using strict delimiters (` ``` `).
*   **Forced JSON:** I do Prompt Engineering by demanding that the AI returns not conversational text, but a strict JSON object with a score from 0.0 to 1.0, so that I can decode it reliably in Python.

---

## 2.3. Image Processing (Computer Vision)
**Reference File:** `backend/app/ml/vision.py`

For diagnoses that rely on x-rays, mammographies, or ultrasound photos (e.g., Breast Cancer or PCOS), I implemented Convolutional Neural Networks (CNNs) using **PyTorch**.

*   **Base Models:** I use proven architectures focused on high precision and low weight (such as ResNet-18).
*   **Vital Pre-Processing:** Different medical imaging equipment generates images of varying colors and contrasts. Before sending to the AI, I apply two techniques in Python using OpenCV (`cv2`):
    1.  **CLAHE:** Normalizes local image contrast to highlight hidden tissue density, microcalcifications, and nodules.
    2.  **Auto-Crop:** Finds the contour of the breast/lesion and crops out dead black background, ensuring the AI focuses only on the relevant biological tissue.
*   **Tensors:** The image is converted from a pixel matrix to normalized Mathematical Tensors before final inference.

---

## 2.4. The Final Decision: Ensemble (Weighted Soft Voting)
**Reference File:** `backend/app/ml/ensemble.py`

With the 3 experts having given their confidence scores (e.g., Tabular = 80%, Text = 90%, Vision = 60%), I need a final decision.

I use an **Ensemble** pattern focused on **Weighted Soft Voting**.

I take the weighted average of the 3 scores, giving different weights depending on the diagnostic reliability of each modality:
*   Example for Cancer: Numerical biopsy and laboratory measurements are the gold standard. I assign **50% weight** to the Tabular data, **25%** to the Medical Image, and **25%** to the Patient's Symptom Narrative.
*   If the patient does not upload an Image (or the Text API fails), the system dynamically recalculates the weights distributing the load proportionally among the remaining active models.

In the end, the Ensemble returns a consolidated score from 0 to 100%, which is formatted and displayed to the clinician on the frontend.

---

## 2.5. Phase 2: Hyperparameter Optimization via Genetic Algorithms (Project 1)
**Reference Directory:** `backend/app/genetic/hyperopt/`

In Phase 2, we replaced manual grid search with a bio-inspired evolutionary engine:
*   **Hybrid Chromosome Representation:** Maps complex search spaces with mixed gene types: discrete integers (`n_estimators`), nullable integers (`max_depth`), continuous floats, base-10 logarithmic floats (`float_log` for $C$, $\gamma$, and `learning_rate` between $10^{-4}$ and $10^{2}$), and categorical choices (`criterion`, `class_weight`).
*   **Clinical Objective Function ($F_2$-Score):** In clinical triage, a **False Negative** (failing to diagnose a sick patient) is far more hazardous than a False Positive. Our objective function weights **Recall** 4 times higher than Precision ($\beta = 2$):
    $$\text{Fitness} = 0.70 \times F_2 + 0.20 \times \text{Recall} + 0.10 \times \text{Accuracy} - \text{Complexity Penalty}$$
*   **Genetic Operators:** Tournament Selection ($k=3$) or Roulette, Hybrid Crossover (Weighted Arithmetic for continuous genes and Uniform for discrete/categorical genes), Gaussian Mutation with domain reflection, and strict Elitism ($E=2$).
*   **Validation:** 5-Fold Stratified Cross-Validation (`StratifiedKFold`) inside a Scikit-Learn `Pipeline` with `StandardScaler` fitted strictly within training folds, ensuring 0% data leakage.
*   **Clinical Impact:** Malignant breast cancer Recall increased from 90.48% (Phase 1 Baseline) to **95.76% (+5.8%)** with an $F_2$-Score of **0.9566 (+4.7%)**.

---

## 2.6. Phase 2: Hospital Logistics & Medical Routing (VRP) with Genetic Algorithms (Project 2)
**Reference Directory:** `backend/app/genetic/routing/`

Hospital logistics presents unique life-critical challenges: urgent deliveries (blood bags, vaccines, post-op dressings) must arrive within strict time windows and cold-chain temperature thresholds (2°C to 8°C).
*   **Modeled Problem:** Capacitated Vehicle Routing Problem with Time Windows and Priority Penalties (CVRP/VRPTW).
*   **Permutation Chromosome & Order Crossover (OX):** Chromosomes encode permutation tours of delivery stops. Order Crossover preserves relative stop orders without generating duplicate or omitted stops.
*   **2-Opt Inversion Mutation:** Inverts sub-sequences of stops to eliminate self-crossing routes and optimize local distance.
*   **Multi-Tier Medical Fitness Evaluation:**
    1. *Clinical Urgency Penalties:* High-priority patients and urgent deliveries receive steep exponential tardiness penalties if served late.
    2. *Vehicle Capacity Constraints:* Overloading vehicle thermal cooler volume/weight (kg) incurs high rejection penalties.
    3. *Maximum Travel Range:* Enforces vehicle battery/fuel limits (km).
    4. *Makespan Minimization:* Balances workload across all active vans to prevent bottlenecking a single team.

---

## 2.7. Clinical Explainability and Logistics Field Assistant via LLMs
**Reference Files:** `backend/app/services/clinical_llm.py` and `backend/app/services/logistics_llm.py`

Large Language Models provide decision-support intelligence for both clinical and logistics workflows:
*   **Medical Diagnostic Explanations:** The LLM receives the patient's laboratory percentiles, biomarker values, and model confidence scores, synthesizing an auditable clinical report with: Diagnostic Summary, Key Risk Factors, Suggested Next Steps, and Ethical Disclaimers.
*   **Field Logistics Itineraries & Executive Reports:** Generates step-by-step driving itineraries with cold-chain compliance alerts and produces executive hospital reports detailing mileage, transit duration, and estimated fuel and $\text{CO}_2$ savings.
*   **LLM Governance & Security:**
    - Active Prompt Injection defenses in Portuguese and English.
    - System prompts strictly enforced in English for higher determinism and lower token footprint.
    - Semantic similarity caching with SHA-256 and Jaccard distance.
    - Offline heuristic fallback engines guaranteeing 100% operational uptime even without internet or API keys.

---

**Next Step:**
To see how the FastAPI Backend ties all these models together and exposes them on the internet, read [3-backend-fastapi.md](./3-backend-fastapi.md).
