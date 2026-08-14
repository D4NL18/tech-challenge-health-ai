# HealthAI - Multimodal Diagnostic Platform

*Read this in other languages: [English](README_en.md) | [Português](README.md)*

Welcome to the **HealthAI** repository. I developed this project as an intensive study object to explore the convergence between Modern Software Engineering and Multimodal Artificial Intelligence.

The platform's goal is to act as a medical triage assistant. Unlike traditional Data Science projects that run only in spreadsheets or notebooks, this is an **end-to-end software product**, featuring a clean Frontend and a structured Backend ready for the web.

## 📚 Study Guide (Documentation)

Since this repository is my study guide, I have documented absolutely all architecture and code decisions. I suggest reading the documents below in order, as they tell the "story" of how the project was built:

1. [Overview and Serverless Architecture](docs_en/1-visao-geral-arquitetura.md)
2. [Deep Dive: Artificial Intelligence Engine](docs_en/2-inteligencia-artificial.md)
3. [Backend and FastAPI](docs_en/3-backend-fastapi.md)
4. [Frontend and Angular](docs_en/4-frontend-angular.md)
5. [MLOps and Training Lifecycle](docs_en/5-mlops-treinamento.md)
6. [Synthetic Test Data](docs_en/6-exemplos-testes.md)

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

# 4. Install the heavy dependencies (PyTorch, FastAPI, Pandas, etc)
pip install -r requirements.txt

# 5. Start the FastAPI server on port 8000
python -m uvicorn app.main:app --reload
```
The API will be running at `http://localhost:8000`. You can access the interactive Swagger documentation at `http://localhost:8000/docs`.

### 2. Running the Frontend (User Interface)
The Frontend requires Node.js (version 18+) and the Angular CLI installed.

```bash
# 1. Access the frontend folder
cd frontend

# 2. Install Node dependencies
npm install

# 3. Start the Angular development server
npm start
```
The graphical interface will automatically open in your browser at `http://localhost:4200`.

---

## 🛠 Technologies Used
*   **Artificial Intelligence**: PyTorch (Vision), Scikit-Learn (Tabular), Google Gemini / OpenAI GPT APIs (NLP).
*   **Backend**: Python, FastAPI, Pydantic, Uvicorn.
*   **Frontend**: Angular 18 (Standalone Components), RxJS, SCSS (BEM Methodology).
