# Build stage
FROM python:3.11-slim AS builder

WORKDIR /app

# Install compilation dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install python packages
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Copy backend source code to builder for model pre-downloading and ONNX conversion
COPY backend /app/backend

# Pre-download and compile Hugging Face models to ONNX formats offline
RUN python -m backend.app.inference.onnx_converter

# Production stage
FROM python:3.11-slim AS runner

WORKDIR /app

# Copy installed libraries from the builder stage
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# Configure local Hugging Face directories to point to local pre-downloaded files
ENV HF_HOME=/app/models
ENV SENTENCE_TRANSFORMERS_HOME=/app/models

# Copy compiled models from the builder stage
COPY --from=builder /app/models /app/models

# Copy remaining source code and data files
COPY backend /app/backend
COPY artifacts /app/artifacts
COPY data /app/data

EXPOSE 8000

# Start command (launches ASGI server)
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
