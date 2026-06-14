# Build stage
FROM python:3.12-slim AS builder

WORKDIR /app

# Install compilation dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install python packages
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Also install loguru
RUN pip install --no-cache-dir --user loguru

# Production stage
FROM python:3.12-slim AS runner

WORKDIR /app

# Copy packages from builder stage
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# Configure huggingface & sentence transformers local cache directories
ENV HF_HOME=/app/models
ENV SENTENCE_TRANSFORMERS_HOME=/app/models

# Copy source code and files
COPY backend /app/backend
COPY artifacts /app/artifacts
COPY models /app/models
COPY data /app/data

EXPOSE 8000

# Start command
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
