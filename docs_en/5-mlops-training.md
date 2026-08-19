# 5. MLOps and Model Training

*Read this in other languages: [English](5-mlops-treinamento.md) | [Português](../docs/5-mlops-treinamento.md)*

This document details the lifecycle of Machine Learning models in this project. It answers the question: *"How does a model go from a data experiment to a software product running on the internet?"*

Since I am handling both the **Data Scientist** and **Software Engineer** roles, I decided to physically separate these responsibilities in the project to prevent things from getting mixed up.

---

## 5.1. The Separation: `training_scripts/` vs `app/ml/`

If you look at the Backend folder structure, you will notice that machine learning exists in two different places. This is intentional.

1.  **`training_scripts/` Folder (The Laboratory):**
    *   This is where I act as a Data Scientist.
    *   It is the "Offline" environment. These files only run on my local computer (or in a Jupyter Notebook on Google Colab/Kaggle with powerful GPUs).
    *   They clean up messy CSV files (Data Cleaning), test thousands of different parameters (*Grid Search*), and spend hours training the Artificial Intelligence.
    *   *Important:* The FastAPI API **never** looks at this folder. It does not exist on the production server.

2.  **`app/ml/` Folder (The Factory):**
    *   This is where I act as a Software Engineer.
    *   In this folder, the AI model no longer "learns" anything. The mathematical brain is already ready and "frozen".
    *   The files here only know how to take a ready model, inject the patient's data, and output a probability.
    *   This is the "Online" environment that runs on Cloud Run.

---

## 5.2. Serialization and Exporting (Creating the "Weights")
When the training over in `training_scripts/` finishes and the AI reaches high accuracy (e.g., 95%), I need to "save" its brain to send it to `app/ml/`.

This process is called **Serialization**.
Trained models become large files that we informally call "Weights".

1.  **Tabular Models (Random Forest, XGBoost):**
    I save the entire pipeline in a binary file using `pickle` or `joblib` (e.g., `modelo_pcos.pkl`). It contains both the logical rules and the pre-processing conveyor belt.
2.  **Deep Learning Models (PyTorch):**
    I save the State Dictionary containing the mathematical matrices of the neurons in a `.pth` file (e.g., `modelo_resnet_cancer.pth`).

---

## 5.3. The Bridge: `weights/` Folder
To put the model on the internet server, I take the `.pkl` or `.pth` file generated locally and copy it to the `backend/app/weights/` folder.

When FastAPI initializes on Cloud Run, it reads the models from this folder to load them into RAM, thus connecting the world of Data Science with Backend Software Engineering.

*(Warning: Since neural network weight files weigh gigabytes, they are usually ignored in `.gitignore` and you need to download them from Google Drive or Google Cloud Storage to run the project locally).*

---

**Next Step:**
Ready to test the system? Access the last module to get synthetic test data created for you in [6-exemplos-testes.md](./6-exemplos-testes.md).
