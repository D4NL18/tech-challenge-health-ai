# HealthAI - Multimodal Diagnostic Platform

*Read this in other languages: [English](README_en.md) | [Português](README.md)*

Welcome to the **HealthAI** repository. I developed this project as an intensive study object to explore the convergence between Modern Software Engineering and Multimodal Artificial Intelligence.

The platform's goal is to act as a medical triage assistant. Unlike traditional Data Science projects that run only in spreadsheets or notebooks, this is an **end-to-end software product**, featuring a clean Frontend and a structured Backend ready for the web.

## 📚 Study Guide & Multi-Phase Documentation

Since this repository is my study guide and Tech Challenge delivery, the documentation is organized in a structured manner:

### Core Technical Documentation:
1. [Overview and Serverless Architecture](docs_en/1-overview-architecture.md) *(Complemented with Phase 2)*
2. [Deep Dive: Artificial Intelligence Engine](docs_en/2-artificial-intelligence.md) *(Complemented with Phase 2)*
3. [Backend and FastAPI](docs_en/3-backend-fastapi.md) *(Complemented with Phase 2)*
4. [Frontend and Angular](docs_en/4-frontend-angular.md) *(Complemented with Phase 2)*
5. [MLOps and Training Lifecycle](docs_en/5-mlops-training.md) *(Complemented with Phase 2)*
6. [Synthetic Test Data & Medical Routing](docs_en/6-test-examples.md) *(Complemented with Phase 2)*

### Phase-Specific Deliverables:
- **Phase 1 (Multimodal Health Diagnosis):**
  - [Official Phase 1 Technical Report](docs_en/fase1/technical-report-phase1.md)
- **Phase 2 (Genetic Algorithms & Medical Routing):**
  - [Official Phase 2 Technical Report (Portuguese)](docs/fase2/relatorio-tecnico-fase2.md)
  - [Video Presentation & Demo Script](docs/fase2/roteiro-video-apresentacao.md)
  - [Genetic Algorithm Benchmarks & 3 Systematic Experiments](docs_en/5-mlops-training.md#56-results-of-the-3-systematic-experiments)

---

## 🔬 Phase 2 Highlights (New Features)

### 1. Hyperparameter Optimization via Genetic Algorithms (Project 1)
- Bio-inspired optimization for clinical screening models (Breast Cancer and PCOS).
- **Clinical Fitness Function:** $0.70 \times F_2\text{-Score} + 0.20 \times \text{Recall} + 0.10 \times \text{Accuracy}$ with tree complexity penalty, minimizing false negatives.
- **3 Systematic Experiments:** **+5.8% gain in Recall** and **+4.7% in $F_2$-Score** compared to the Phase 1 GridSearch baseline.
- **Clinical LLM Reports:** `POST /api/v1/anamnesis/explain-diagnosis` providing structured medical justifications.

### 2. Medical Routing with Real Road Graphs via OSRM (Project 2)
- Dedicated frontend route: **`/routes`** (`http://localhost:4200/routes`).
- **OpenStreetMap & OSRM (Zero API Cost):** Fast road distance and time matrix calculation without risking quota exhaustion or requiring paid API keys.
- **Smart Local SQLite Caching (`geo_cache.db`):** Sub-millisecond (< 1ms) response for previously calculated coordinate pairs.
- **Genetic Algorithm VRP (Vehicle Routing Problem):** Handles time windows, clinical urgency/priority weights, and tardiness penalties.
- **Interactive Leaflet.js Map:** Real-time visualization of medical depot, sequenced stops, and driving polylines.
- **Field Team LLM Assistant & Hospital Audit Reports:** Chat-driven field operational guidance and executive impact reporting.

---

## 🚀 How to Run the Project Locally

The repository is a **Monorepo**, containing both the Frontend and the Backend. You will need two open terminals to run the complete application.

### 1. Running the Backend (API and AI Engine)
The Backend requires Python installed on your machine (version 3.9+ recommended).

```bash
# 1. Access the backend folder
cd backend

# 2. (Optional, but recommended) Create a virtual environment
python -m venv venv

# 3. Activate the virtual environment
# On Windows:
.\venv\Scripts\activate
# On Linux/Mac:
source venv/bin/activate

# 4. Install dependencies (PyTorch, FastAPI, Pandas, DEAP, etc)
pip install -r requirements.txt

# 5. (Optional) Run the 3 Genetic Algorithm hyperparameter experiments
python training_scripts/train_genetic_hyperopt.py

# 6. Run automated test suite for Phase 1 & Phase 2 (27 tests)
python -m pytest tests/ -v

# 7. Start the FastAPI server on port 8000
python -m uvicorn app.main:app --reload
```
The API will run at `http://localhost:8000`. Access the interactive Swagger documentation at `http://localhost:8000/docs`.

### 2. Running the Frontend (User Interface)
The Frontend requires Node.js (version 18+) and Angular CLI.

```bash
# 1. Access the frontend folder
cd frontend

# 2. Install Node dependencies
npm install

# 3. Start Angular development server
npm start
```
The interface opens at `http://localhost:4200`:
- **Multimodal Diagnostic Triage:** `http://localhost:4200/` or `http://localhost:4200/dashboard`
- **Medical Routing Module (Phase 2):** `http://localhost:4200/routes`
- **Admin Dashboard & GA Audit:** `http://localhost:4200/admin` (or `http://localhost:4200/admin/dashboard`)

---

## 🛠 Tech Stack
*   **Genetic Algorithms & AI**: Custom Genetic Algorithms (DEAP/Custom), PyTorch (Vision ResNet-18), Scikit-Learn (Random Forest, XGBoost), LLMs (Google Gemini 1.5 Flash / OpenAI GPT-4o-mini).
*   **Logistics & Geo**: OSRM (Open Source Routing Machine), OpenStreetMap, Leaflet.js, SQLite Geo Caching.
*   **Backend**: Python 3.12, FastAPI, Pydantic v2, Uvicorn, Pytest.
*   **Frontend**: Angular 18 (Standalone Components), Leaflet.js, RxJS, SCSS (BEM Design System).
