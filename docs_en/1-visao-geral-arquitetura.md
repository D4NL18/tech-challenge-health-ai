# 1. Overview and Architecture

*Read this in other languages: [English](1-visao-geral-arquitetura.md) | [Português](../docs/1-visao-geral-arquitetura.md)*

This document explains the fundamental architectural choices I made to build the **HealthAI** platform. Since I developed this project alone with a focus on studying and cost efficiency, I opted for a **Serverless** infrastructure on Google Cloud Platform (GCP).

The main goal of this architecture is to guarantee **very low cost**, high availability, and a clear separation of responsibilities (Frontend vs Backend).

---

## 1.1. The Problem with Traditional Architectures
In traditional Machine Learning (ML) systems, companies rent robust machines with GPUs and managed databases (like PostgreSQL or Kubernetes) that stay on 24 hours a day.

Since this is an academic/personal project, paying hundreds of dollars a month just to keep AI models available makes no sense.

## 1.2. The Solution: "Low-Cost" Serverless Architecture
To solve the cost issue, I designed a **100% Serverless** architecture based on Google Cloud's *Free Tiers*.

In this model, I only "pay" (or consume free quota) for the exact milliseconds a request is being processed. If no one accesses the system at night, the instances are turned off (Scale to Zero).

The separation of responsibilities was established as follows:

1.  **Frontend (Angular)** hosted on **Firebase Hosting**.
2.  **Backend and AI Engine (FastAPI)** hosted on **Google Cloud Run**.

---

## 1.3. Why Angular on the Frontend?
I chose Angular because it is an extremely structured and robust framework.
Unlike generating screens within Python (such as using Jinja2 or Django Templates), Angular allows me to create a **Single Page Application (SPA)**.

This means the browser downloads all the HTML/CSS/JS code at once. When the patient navigates between the Anamnesis and Dashboard screens, the transition is instantaneous and asynchronous, without reloading the page.

**Hosting (Firebase Hosting):**
Since Angular generates only static files at the end of the *build* process, I don't need a running server. I host these static files on Firebase Hosting, which has a generous free tier, global CDN, and automatically configured SSL certificate.

---

## 1.4. Why FastAPI on the Backend?
The heart of the platform is the Artificial Intelligence engine. I needed a backend in Python (since 99% of ML libraries like PyTorch, Scikit-Learn, and Pandas are in Python).

I chose **FastAPI** over Flask or Django for the following reasons:

1.  **Asynchronous by Default (ASGI):** The system communicates over the internet with Gemini and GPT APIs. FastAPI is excellent at not blocking the server while waiting for slow network responses.
2.  **Strict Validation (Pydantic):** In healthcare systems, incorrect data leads to dangerous diagnoses. FastAPI validates data types automatically using Pydantic, instantly rejecting malformed requests.
3.  **Speed:** It is one of the fastest Python frameworks available, rivaling NodeJS and Go.

**Hosting (Cloud Run):**
I place this FastAPI server inside a *Docker Container* and deploy it to **Google Cloud Run**. Cloud Run charges only for the seconds the API is processing medical inference.

---

## 1.5. Stateless Architecture
To keep everything simple and cheap, I made a crucial architectural decision: **the system is Stateless**.

This means that:
*   I **do not** have an SQL database (like MySQL or Postgres).
*   I **do not** keep a long-term history of patient diagnoses.
*   I **do not** save passwords or do heavy user account management in a database.

The platform acts purely as an "Advanced Calculator". Angular sends the clinical data; FastAPI receives it, loads the model weights into RAM, performs the calculation, returns the final diagnostic response, and immediately **forgets** who made the request.

This approach focuses 100% on the Artificial Intelligence algorithm, enormously reducing the vulnerability surface (leakage of medical data) and infrastructure costs.

---

**Next Step:**
To deeply understand how the AI makes decisions behind the scenes, read the document [2-inteligencia-artificial.md](./2-inteligencia-artificial.md).
