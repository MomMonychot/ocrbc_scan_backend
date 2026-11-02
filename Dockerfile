# ==============================================================================
# Multi-Stage Secure Dockerfile for District Administration OCR Platform
# Zero Data Retention Architecture: Non-root execution, ephemeral memory buffers
# ==============================================================================

FROM python:3.11-slim AS base

# Prevent Python from writing .pyc files to disk and enable unbuffered logging
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/workspace

# Install essential system dependencies required for OpenCV and C extensions
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create dedicated non-privileged user and group for hardened container execution
RUN groupadd -g 10001 appgroup && \
    useradd -u 10001 -g appgroup -s /bin/bash -m appuser

WORKDIR /workspace

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy backend application source code
COPY --chown=appuser:appgroup . /workspace

# Ensure backend package symlink exists for module compatibility
RUN ln -sf app backend

# Switch to non-root user
USER appuser

# Default port for web API
EXPOSE 8003

# Default entrypoint (overridden in docker-compose for celery_worker)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8003"]
