# 2. Artificial Intelligence Engine (Deep Dive)

*Read this in other languages: [English](2-inteligencia-artificial.md) | [Português](../docs/2-inteligencia-artificial.md)*

In this document, I explain in detail how I structured the "Brain" of the platform. Medicine is complex, and relying on a single type of data (only text, or only image) is dangerous.

Therefore, I built a **Multimodal** system based on the union of 3 pillars of Artificial Intelligence: **Classic Machine Learning (Tabular)**, **Natural Language Processing (Text)**, and **Computer Vision (Image)**.

---

## 2.1. Tabular Processing (Classic Machine Learning)
**Reference File:** `backend/app/ml/tabular.py`

When the patient fills out the form answering direct questions (e.g., Age, Weight, Height, if the pain increases), they are generating **Structured Data**.

For this type of numerical and categorical data, deep neural networks often suffer from *Overfitting* (memorizing the data instead of learning). Therefore, I opted for classic algorithms based on Decision Trees, such as **Random Forest** or **XGBoost**, as well as **Logistic Regression**.

*   **Advantage:** They are extremely lightweight algorithms. They do not require a GPU to perform inference.
*   **Pipeline (Pickle):** Before the algorithm runs, the patient's data needs to be normalized (e.g., go through a `StandardScaler`). I export this entire training "conveyor belt" (Pipeline) into a binary `.pkl` file using the `pickle` or `joblib` library, and FastAPI just loads it into RAM and executes it.
*   **Predict Proba:** Instead of asking the model to just say if the patient is "Sick" or "Healthy", I use the `predict_proba()` function. It returns a **mathematical percentage** of confidence (e.g., 82% chance), essential for my final voting system.

---

## 2.2. Text Processing (Natural Language Processing - NLP)
**Reference File:** `backend/app/ml/text.py`

Closed-ended questions cannot capture nuances like "I feel a sharp pain in my head that radiates to my neck when I lie down". For this, I opened an "Extra Symptoms" field for the patient to type free text.

*   **Large Language Models (LLMs):** To extract meaning from the text, I send the string to commercial LLMs via API.
*   **Fallback Chain (High Availability):** AI APIs can go down or be slow. I implemented a technique called *Graceful Degradation*. The system tries to use Google Gemini 3.6; if it fails, it falls back to Gemini 3.5; if the entire Google API is down, it automatically switches to OpenAI (GPT).
*   **Security (Prompt Injection):** To prevent malicious users from "hypnotizing" the AI (e.g., asking for drug recipes), I isolate the system instruction from the user input using strict delimiters (```).
*   **Forced JSON:** I do Prompt Engineering by demanding that the AI returns not spoken text, but a strict JSON object with a score from 0.0 to 1.0, so that I can decode it in Python.

---

## 2.3. Image Processing (Computer Vision)
**Reference File:** `backend/app/ml/vision.py`

For diagnoses that rely on x-rays, MRIs, or photos (e.g., Breast Cancer or Melanoma), I implemented Convolutional Neural Networks (CNNs) using **PyTorch**.

*   **Base Models:** I use famous architectures focused on high precision and low weight (such as ResNet, DenseNet, or EfficientNet).
*   **Vital Pre-Processing:** Different X-Ray machines generate images of different colors and contrasts. Before sending to the AI, I apply two techniques in Python using OpenCV (`cv2`):
    1.  **CLAHE:** Normalizes the image contrast to highlight hidden veins and nodules.
    2.  **Auto-Crop:** Finds the edges of the breast/tumor and cuts out all the "dead" black background, ensuring the AI focuses only on the relevant tissue.
*   **Tensors:** The image is converted from a pixel matrix to normalized Mathematical Tensors before final inference.

---

## 2.4. The Final Decision: Ensemble (Weighted Soft Voting)
**Reference File:** `backend/app/ml/ensemble.py`

With the 3 experts having given their confidence score (e.g., Tabular = 80%, Text = 90%, Vision = 60%), I need a final decision.

I use an **Ensemble** pattern focused on **Weighted Soft Voting**.

I take the mathematical average of the 3 scores, but I give different "weights" depending on the reliability of the source.
*   Example for Cancer: Numerical lab data is usually the pillar of truth. I give **50% weight** to the Tabular data, **25%** to the X-Ray, and **25%** to the patient's Report.
*   If the patient does not send the Image (or the Text API fails), the system recalculates the weights distributing the load among the surviving models.

In the end, the Ensemble returns a score from 0 to 100%, which is formatted and sent to the Frontend to be displayed to the doctor!

---

**Next Step:**
To see how the FastAPI Backend ties all these models together and exposes them on the internet, read [3-backend-fastapi.md](./3-backend-fastapi.md).
