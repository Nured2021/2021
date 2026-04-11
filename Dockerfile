# ORD AI — Production Docker Image
FROM python:3.12-slim

# System dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl sqlite3 && \
    rm -rf /var/lib/apt/lists/*

# Non-root user for security
RUN useradd -m -s /bin/bash ordai
WORKDIR /app

# Install Python dependencies first (layer cache)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY --chown=ordai:ordai . .

# Runtime directories (persistent volume mount point)
RUN mkdir -p /data && chown ordai:ordai /data

USER ordai

# Override all SQLite paths to /data so they survive container restarts
ENV ORD_AI_DATA_DIR=/data
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

EXPOSE 5000

# Eventlet-based production server (handles WebSockets natively)
CMD ["python", "-u", "app.py"]
