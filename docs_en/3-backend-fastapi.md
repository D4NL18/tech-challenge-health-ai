# 3. Backend and FastAPI (Software Engineering)

*Read this in other languages: [English](3-backend-fastapi.md) | [Português](../docs/3-backend-fastapi.md)*

In this document, I focus purely on Software Engineering. I explain how I structured the Python Backend to handle network calls, manage memory intelligently, validate data, and orchestrate evolutionary optimization and LLMs.

The project structure follows the **MVC (Model-View-Controller) pattern adapted for Services**, promoting a clear separation of concerns.

---

## 3.1. Directory Structure and Responsibilities

```text
backend/app/
├── main.py                       # Entrypoint: Starts the server, manages CORS and lifespan warm-up.
├── api/routers/
│   ├── anamnesis.py              # Diagnostic controllers, LLM explainability, and GA admin stats.
│   └── routes_router.py          # Hospital logistics, OSRM routing, driver guides, and chat.
├── models/schemas.py             # DTOs: Strict Pydantic input and output schemas.
├── services/
│   ├── inference.py              # Facade orchestrating multimodal ML inference.
│   ├── clinical_llm.py           # Medical report synthesis with prompt injection defenses.
│   ├── logistics_llm.py          # Turn-by-turn driver instructions and executive reports.
│   └── geo/
│       ├── osrm_provider.py      # OpenStreetMap OSRM client with Haversine fallback.
│       └── geo_cache.py          # Persistent SQLite cache for distance/duration matrices.
├── genetic/
│   ├── hyperopt/                 # Project 1: Evolutionary hyperparameter tuning engine.
│   └── routing/                  # Project 2: Evolutionary VRP solver for medical logistics.
└── ml/                           # Frozen models and multimodal predictors.
    ├── tabular.py                # Tabular inference with predict_proba.
    ├── text.py                   # NLP symptom narrative analysis.
    ├── vision.py                 # PyTorch ResNet-18 computer vision.
    └── ensemble.py               # Weighted soft voting aggregator.
```

### The Request Flow:
1. Angular sends the request payload.
2. The **Router** (`anamnesis.py` or `routes_router.py`) receives the HTTP call.
3. The **Schema** (`schemas.py`) validates that all input types match expected constraints.
4. The Router delegates processing to the appropriate **Service Layer**.
5. The Service coordinates the **ML/GA Engines** (`ml/` or `genetic/`).
6. The models return results, and the Service packages them into a clean JSON response for the Frontend.

---

## 3.2. Memory Management (Lifespan / Cold Start)
**Reference File:** `backend/app/main.py`

Machine Learning models (like a PyTorch convolutional network) rely on large weight matrices stored in `.pth` or `.pkl` files on disk. Reading these gigabyte-scale files into RAM takes several seconds.

If this loading happened on every request, latency would be unacceptable.

**The Solution:** We use FastAPI's `@asynccontextmanager` **Lifespan** handler:
When Cloud Run boots the container (or during local startup), `main.py` intercepts the initialization event, loads model weights into RAM (Warm-up), and initializes singletons. When user requests arrive, the models are already hot and respond in milliseconds.

---

## 3.3. Strict Data Validation (Pydantic v2)
**Reference File:** `backend/app/models/schemas.py`

FastAPI provides native integration with **Pydantic v2**.
In `schemas.py`, we define Data Transfer Objects (DTOs) with strict type hints (`str`, `int`, `float`, `Optional`).

If a request contains invalid types or values out of acceptable clinical ranges, Pydantic intercepts the payload before it touches business logic, immediately returning an HTTP 422 (Unprocessable Entity) response with exact error locations.

---

## 3.4. Multipart Form-Data vs JSON
**Reference File:** `backend/app/api/routers/anamnesis.py`

Standard REST APIs communicate via `application/json`. However, multimodal triage requires uploading binary image files (X-Rays, ultrasounds) alongside structured clinical measurements.

We adopt the **Multipart/Form-Data** standard:
*   The raw image file is received via the `image` field.
*   The structured patient data is received via the `anamnesis_data` field as a JSON string.
*   Python deserializes the string via `json.loads` and validates it against Pydantic schemas.

This enables transferring tabular symptoms and high-resolution medical images in a single atomic HTTP request.

---

## 3.5. Phase 2 Evolution: Medical Routes Router (`routes_router.py`)
**Reference File:** `backend/app/api/routers/routes_router.py`

In Phase 2, a comprehensive asynchronous medical logistics pipeline was introduced:
1. `GET /api/v1/routes/demo-scenario`: Returns a realistic benchmark demonstration scenario with a central medical depot and distributed patient stops across Salvador / São Paulo.
2. `GET /api/v1/routes/geocode`: Direct and reverse geocoding powered by local SQLite caching.
3. `POST /api/v1/routes/optimize`: Receives depot, deliveries (with clinical urgency tiers and time windows), fleet specs, and GA hyperparameters. Solves the VRP over the real road graph via OSRM and returns sequenced routes with encoded polylines and detailed telemetry.
4. `POST /api/v1/routes/instructions`: Generates turn-by-turn driving instructions for field personnel with cold-chain maintenance warnings (2°C to 8°C).
5. `POST /api/v1/routes/report`: Produces an executive hospital audit report analyzing travel time, mileage, route efficiency, and fleet safety.
6. `POST /api/v1/routes/chat`: Operational logistics chat assistant for drivers and dispatchers in transit.

Additionally, `anamnesis.py` was expanded with:
- `POST /api/v1/anamnesis/explain-diagnosis`: Synthesizes an explainable clinical report via LLM (Gemini / OpenAI with an offline heuristic fallback).
- `GET /api/v1/anamnesis/admin/genetic-experiments`: Historical benchmark comparison across the 3 Genetic Algorithm hyperparameter calibration experiments.

---

## 3.6. Geo Layer & OSRM Provider with Local SQLite Caching
**Reference Files:** `backend/app/services/geo/osrm_provider.py` and `backend/app/services/geo/geo_cache.py`

To eliminate third-party API costs and prevent quota exhaustion, we use **OSRM (Open Source Routing Machine) over OpenStreetMap**:
- **Zero Paid Quota:** Completely free and open routing engine with automatic mathematical fallback to Haversine distance if network issues occur.
- **Persistent SQLite Cache (`backend/data/geo_cache.db`):** Stores $N \times N$ duration and distance matrices indexed by coordinate hashes. Repeated requests for identical coordinate sets respond instantly in less than 1ms without outbound network calls.
- **Two-Stage Optimization:** The Genetic Algorithm executes thousands of evolutionary iterations in memory using cached travel matrices. Only the final optimal route triggers a single `/route/v1/driving` call to retrieve the detailed visualization polyline.

---

## 3.7. Clinical and Logistics LLMs with Resilient Heuristics
**Reference Files:** `backend/app/services/clinical_llm.py` and `backend/app/services/logistics_llm.py`

Language models assist clinical decision-making and operational logistics:
- Dynamic multi-provider integration supporting Google Gemini (`gemini-1.5-flash`) and OpenAI (`gpt-4o-mini`).
- **Complete Offline Resilience:** If API keys are unset or network connectivity is lost, the system gracefully degrades to expert heuristic engines. These generate structured, medically sound clinical reports and operational routing instructions without throwing unhandled exceptions.

---

**Next Step:**
To see how the Angular Frontend consumes these endpoints and renders the user experience, access [4-frontend-angular.md](./4-frontend-angular.md).
