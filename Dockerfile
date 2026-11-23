# Deploy ke SnapDeploy / Render / container Docker mana pun.
# Backend + frontend disajikan dari satu container yang sama.
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Install dulu supaya layer dependency ter-cache saat kode diubah.
COPY backend/requirements.txt ./backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt

COPY backend ./backend
COPY frontend ./frontend

# SnapDeploy/Render menyetel PORT otomatis. Default 8000 untuk lokal.
WORKDIR /app/backend
EXPOSE 8000

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
