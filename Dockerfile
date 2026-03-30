# ISO 27001 & ITIL Evaluator - Dockerfile
# Build: docker build -t iso27001-evaluator .
# Run:   docker-compose up -d

FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create non-root user for security
RUN useradd -m -u 1000 appuser

# Copy application code
COPY app/ ./app/
COPY scripts/ ./scripts/
COPY docs/ ./docs/

# Create necessary directories
RUN mkdir -p /app/uploads /app/backups /app/backups/auto /app/backups/deploy /app/backups/rfc /app/backups/manual \
    && chown -R appuser:appuser /app

# Set permissions
RUN chmod +x /app/scripts/*.py

USER appuser

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PATH="/home/appuser/.local/bin:$PATH"

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
