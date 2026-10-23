# 6. Unseen Test Examples (Triage & Routing)

*Read this in other languages: [English](6-test-examples.md) | [Português](../docs/6-exemplos-testes.md)*

To test model accuracy and verify that all pipelines explained in previous documents operate correctly, we provide synthetic clinical and logistics test cases.

You can paste these values into the Angular Frontend or query endpoints directly. Because these synthetic data points were not present in original training splits, they demonstrate model generalization on unseen data.

---

## 6.1. Breast Cancer

### Example A: High Risk (Malignant)
*Synthetic measurements designed with pronounced features typical of malignant tissue (larger volume, irregular texture, high concavity).*
- **Mean Radius**: 21.35
- **Mean Texture**: 24.12
- **Mean Compactness**: 0.2985
- **Mean Concavity**: 0.3210
- **Mean Concave Points**: 0.1652
- **Radius SE**: 1.250
- **Perimeter SE**: 9.150
- **Area SE**: 185.3
- **Concavity SE**: 0.0621
- **Worst Radius**: 28.50
- **Worst Texture**: 31.05
- **Worst Smoothness**: 0.1785
- **Worst Compactness**: 0.7231
- **Worst Concavity**: 0.7854
- **Worst Concave Points**: 0.2891
- **Worst Symmetry**: 0.5102

### Example B: Low Risk (Benign)
*Synthetic measurements designed with characteristics typical of benign findings (smaller dimensions, smooth margins, low concavity).*
- **Mean Radius**: 11.45
- **Mean Texture**: 13.10
- **Mean Compactness**: 0.0652
- **Mean Concavity**: 0.0315
- **Mean Concave Points**: 0.0215
- **Radius SE**: 0.1850
- **Perimeter SE**: 1.350
- **Area SE**: 15.20
- **Concavity SE**: 0.0152
- **Worst Radius**: 12.85
- **Worst Texture**: 16.45
- **Worst Smoothness**: 0.1150
- **Worst Compactness**: 0.1350
- **Worst Concavity**: 0.1052
- **Worst Concave Points**: 0.0651
- **Worst Symmetry**: 0.2510

---

## 6.2. Polycystic Ovary Syndrome (PCOS)

### Example C: High Risk (PCOS = Yes)
*Synthetic patient presenting clinical signs of hyperandrogenism and endocrine imbalance (elevated LH relative to FSH).*
- **Weight (Kg)**: 82.5
- **Height (cm)**: 162.0
- **Recent Weight Gain?**: Yes
- **Unusual Hair Growth?**: Yes
- **Skin Darkening?**: Yes
- **Frequent Fast Food Consumption?**: Yes
- **Cycle Length (Days)**: 7
- **RBS (Blood Sugar)**: 110.5
- **FSH (mIU/mL)**: 4.10
- **LH (mIU/mL)**: 9.35
- **TSH (mIU/L)**: 3.20
- **Progesterone (PRG)**: 0.25
- **Follicle No. (Left)**: 25
- **Follicle No. (Right)**: 16

### Example D: Low Risk (PCOS = No)
*Synthetic patient with balanced hormonal profile and absence of physical syndrome indicators.*
- **Weight (Kg)**: 58.0
- **Height (cm)**: 168.0
- **Recent Weight Gain?**: No
- **Unusual Hair Growth?**: No
- **Skin Darkening?**: No
- **Frequent Fast Food Consumption?**: No
- **Cycle Length (Days)**: 4
- **RBS (Blood Sugar)**: 85.0
- **FSH (mIU/mL)**: 6.80
- **LH (mIU/mL)**: 3.10
- **TSH (mIU/L)**: 1.80
- **Progesterone (PRG)**: 0.95
- **Follicle No. (Left)**: 6
- **Follicle No. (Right)**: 5

---

## 6.3. Test Scenario: Medical Routing in São Paulo (Phase 2)

To evaluate the Medical Routing module (`/routes`), you can use the "Load Demo Scenario" button on the UI or submit the following parameters to the API:

### Central Distribution Depot / Primary Health Center:
- **Name**: UBS Vila Mariana (Central Base)
- **Coordinates**: `[-23.5895, -46.6348]`

### Patient Home Care Deliveries:
1. **Dona Lurdes (Oncology / Post-Op Wound Dressing)**:
   - Coordinates: `[-23.6498, -46.7032]` (Santo Amaro)
   - Priority: High (Weight 10) | Time Window: 08:00 - 10:30
2. **Sr. João (Cardiac Telemetry Monitoring)**:
   - Coordinates: `[-23.6821, -46.6743]` (Cidade Dutra)
   - Priority: Medium (Weight 5) | Time Window: 09:00 - 12:00
3. **Dona Maria (Routine Blood Sample Collection)**:
   - Coordinates: `[-23.5431, -46.5312]` (Tatuapé)
   - Priority: Regular (Weight 2) | Time Window: 10:00 - 14:00
4. **Criança Enzo (IV Pediatric Antibiotic Therapy)**:
   - Coordinates: `[-23.5182, -46.6021]` (Vila Maria)
   - Priority: High (Weight 9) | Time Window: 08:30 - 11:00
5. **Sr. Benedito (Diabetic Suture & Urgent Care)**:
   - Coordinates: `[-23.5612, -46.6558]` (Bela Vista)
   - Priority: Critical Urgency (Weight 12) | Time Window: 07:30 - 09:30
6. **Dona Francisca (Respiratory Physiotherapy)**:
   - Coordinates: `[-23.6015, -46.6912]` (Brooklin)
   - Priority: Regular (Weight 4) | Time Window: 13:00 - 16:00

The Genetic Algorithm automatically sequences Sr. Benedito, Dona Lurdes, and Criança Enzo in the early morning slots while minimizing total road mileage across the OSRM street network.

---

## 6.4. Automated Test Suite (Pytest)

The project includes an end-to-end automated testing suite with complete coverage for Phase 1 and Phase 2 modules, totaling **27 unit and integration tests**.

### Test Modules:
1. `backend/tests/test_genetic_hyperopt.py` (5 tests):
   - Chromosome gene bounds (`int`, `float`, `float_log`, `cat`) and Scikit-Learn estimator decoding.
   - Gaussian mutation, arithmetic/uniform crossover, and tournament selection operators.
   - Clinical fitness evaluation with $F_2$-score in stratified folds without data leakage.
   - Multi-model search spaces (Random Forest, SVM, Gradient Boosting, MLP, KNN, Logistic Regression).
   - Real-time convergence visualizer telemetry updates.
2. `backend/tests/test_vrp_routing.py` (7 tests):
   - VRP permutation chromosome, Order Crossover (OX), and 2-opt inversion mutation.
   - Genetic solver respecting thermal load capacity and service time windows.
   - Clinical urgency distribution and makespan minimization.
   - Strict vehicle assignment and 3-tier priority balancing (Critical, High, Regular).
   - Dwell times and traffic multiplier integration.
3. `backend/tests/test_traffic_model.py` (4 tests):
   - Dynamic traffic multipliers across municipal tiers (Metropolises, State Capitals, Medium Cities).
   - Rush-hour peak differentiation (07:00-09:30 and 17:30-19:30) vs. off-peak hours.
   - Congestion attenuation along expressways and beltways.
   - Transit clock parsing and formatting (HH:MM).
4. `backend/tests/test_osrm_cache.py` (2 tests):
   - Local SQLite database persistence (`geo_cache.db`).
   - Matrix dimensional consistency and fault-tolerant Haversine fallback.
5. `backend/tests/test_routes_api.py` (4 tests):
   - Demo scenario endpoint (`GET /api/v1/routes/demo-scenario`).
   - Asynchronous route optimization (`POST /api/v1/routes/optimize`).
   - Driver turn-by-turn instructions (`POST /api/v1/routes/instructions`) and executive report (`POST /api/v1/routes/report`).
   - Diagnostic explainability endpoint (`POST /api/v1/anamnesis/explain-diagnosis`).
6. `backend/tests/test_llm_governance.py` (5 tests):
   - Active bilingual Prompt Security Guard blocking prompt injection attempts in Portuguese and English.
   - Semantic similarity caching for LLM invocations.
   - Strict English system prompts enforcement for determinism and token efficiency.
   - Resilient fallback chains degrading gracefully to domain-expert heuristic generators.
   - Security validation and formatting checks on clinical reports and logistics instructions.

### How to Execute the Full Test Suite:
```bash
cd backend
python -m pytest tests/ -v
```
**Official Result:** 27 passed (100% success rate in ~50s).
