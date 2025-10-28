FROM python:3.11-slim AS builder

WORKDIR /build

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

FROM python:3.11-slim

RUN useradd -m -u 1000 appuser
RUN mkdir -p /app && chown appuser:appuser /app

WORKDIR /app

COPY --from=builder /root/.local /home/appuser/.local

# Copy the entire api directory to maintain package structure
COPY --chown=appuser:appuser api/ ./api/

ENV PATH=/home/appuser/.local/bin:$PATH
ENV PYTHONPATH=/app

USER appuser

EXPOSE 8000

# Run from parent directory so imports work
WORKDIR /app
CMD ["python", "-m", "api.main"]
