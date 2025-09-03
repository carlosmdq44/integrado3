# Dockerfile
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Paquetes mínimos del sistema (liviano)
RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential curl && \
    rm -rf /var/lib/apt/lists/*

# Solo requirements primero (cache de capas)
COPY requirements.txt .

# Instala dependencias de Python (las tuyas)
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos el código (sin data; esa la montamos como volumen)
COPY run.py ./run.py
COPY scripts ./scripts
# Si tenés carpetas extra, descomenta:
# COPY config ./config
# COPY sql ./sql

# EntryPoint para que puedas pasar la ruta al CSV como argumento
ENTRYPOINT ["python", "run.py"]