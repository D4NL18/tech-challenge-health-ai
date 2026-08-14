# 3. Backend and FastAPI (Software Engineering)

*Read this in other languages: [English](3-backend-fastapi.md) | [Português](../docs/3-backend-fastapi.md)*

In this document, I will focus purely on Software Engineering. I explain how I structured the Python Backend to handle network calls, manage memory intelligently, and validate data.

The project structure follows the **MVC (Model-View-Controller) pattern adapted for Services**, promoting a separation of responsibilities.

---

## 3.1. Directory Structure and Responsibilities

```text
backend/app/
├── main.py                    # Entrypoint: Starts the server, manages CORS and the lifecycle.
├── api/routers/anamnesis.py   # Controllers: Exposes HTTP endpoints (the API URLs).
├── models/schemas.py          # DTOs: Defines strict input and output "molds" (Pydantic).
├── services/inference.py      # Service Layer (Facade): Orchestrates the AI models.
└── ml/                        # Isolated AI Engines.
    ├── tabular.py             
    ├── text.py              
    ├── vision.py              
    └── ensemble.py            
```

### The Request Flow:
1. Angular sends the data.
2. The **Router** (`anamnesis.py`) receives the HTTP call.
3. The **Schema** (`schemas.py`) validates if the data is correct (e.g., if "Age" is an integer).
4. If valid, the Router passes the problem to the **Service** (`inference.py`).
5. The Service acts as a manager. It doesn't know how to calculate anything, but it knows how to call the **ML Experts** (`ml/`).
6. The models calculate the scores, the Service receives them back, and packages them into a standardized JSON object for the Frontend.

---

## 3.2. Memory Management (Lifespan / Cold Start)
**Reference File:** `backend/app/main.py`

This is the most important performance concept of the application.
Machine Learning models (like a PyTorch neural network) are heavy. They rely on giant mathematical matrices (weights) saved in `.pth` or `.pkl` files on the HDD.

Loading gigabytes from the HDD into RAM is an I/O operation that takes *seconds*.
If I did this loading every time a patient clicked "Diagnose", the API would be unbearably slow.

**The Solution:** I use the FastAPI `@asynccontextmanager` feature called **Lifespan**.
When I type `npm start` (or Cloud Run starts the container), `main.py` intercepts the initialization event. It opens the `.pkl` and `.pth` files, loads the matrices into RAM (Warm-up), and leaves them there.
When requests arrive, the AI is already "awake" and responds in milliseconds.

---

## 3.3. Strict Data Validation (Pydantic)
**Reference File:** `backend/app/models/schemas.py`

FastAPI's main advantage over Flask is its deep integration with **Pydantic**.
In `schemas.py`, I create Data Classes (DTOs - Data Transfer Objects). I define exactly which fields the Frontend is required to send, and what type they are (`str`, `int`, `float`, `Optional`).

If the Frontend tries to send "twenty years" in a field that expects the number `20`, Pydantic intercepts the error before it even reaches the Artificial Intelligence and immediately returns a 422 Error (Unprocessable Entity) stating exactly which field was wrong.

This prevents the platform from crashing or generating a bizarre diagnosis due to "dirty" data.

---

## 3.4. Multipart Form-Data vs JSON
**Reference File:** `backend/app/api/routers/anamnesis.py`

REST APIs usually use the `application/json` format to transmit data. But I have a problem: **I need to send the X-Ray photo**.
JSON was not made to transmit heavy binary files efficiently.

To solve this, I use the **Multipart/Form-Data** pattern in the Controller.
*   I receive the raw image file in the `image` field.
*   I receive all the clinical text data in the `anamnesis_data` field as a large String.
*   In Python, I use `json.loads` to convert this String back into a Dictionary, and pass it to Pydantic for validation.

Thus, in a single network request, I send both the tabular data and the Image.

---

**Next Step:**
To understand how I structured the Frontend that consumes this API, access [4-frontend-angular.md](./4-frontend-angular.md).
