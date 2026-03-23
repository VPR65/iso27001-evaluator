FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN useradd -m appuser

COPY app/ ./app/
COPY scripts/ ./scripts/

RUN mkdir -p /app/uploads /app/backups /app/backups/auto /app/backups/deploy /app/backups/rfc /app/backups/manual
RUN chown -R appuser:appuser /app

USER appuser

ENV PYTHONUNBUFFERED=1
ENV DATABASE_URL=sqlite:///./iso27001.db

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
