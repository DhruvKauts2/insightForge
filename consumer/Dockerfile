# Multi-stage build for consumer
FROM python:3.11-slim as builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy parent requirements
COPY ../requirements.txt .

RUN pip install --user --no-cache-dir -r requirements.txt

# Production stage
FROM python:3.11-slim

RUN useradd -m -u 1000 appuser && \
    mkdir -p /app && \
    chown -R appuser:appuser /app

WORKDIR /app

COPY --from=builder /root/.local /home/appuser/.local
COPY --chown=appuser:appuser consumer.py .

ENV PATH=/home/appuser/.local/bin:$PATH

USER appuser

CMD ["python", "consumer.py"]
