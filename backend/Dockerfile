FROM python:3.10-slim

WORKDIR /app

# Instalar pacotes de sistema necessários (ex: opencv-python-headless precisa do libglib2.0-0)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar os requerimentos e instalá-los primeiro para usar o cache do Docker
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar a pasta app, weights e scripts de treinamento (necessários para os modelos importarem as classes corretas)
COPY app/ ./app/
COPY weights/ ./weights/
COPY training_scripts/ ./training_scripts/

# Expor a porta 8080 (padrão do Cloud Run)
EXPOSE 8080

# Iniciar o servidor Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
