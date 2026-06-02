# Multi-stage build for Agentic AI Framework Generator
FROM python:3.11-slim as builder

WORKDIR /build

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Final stage
FROM python:3.11-slim

WORKDIR /app

# Install runtime system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy Python dependencies from builder
COPY --from=builder /root/.local /root/.local

# Ensure pip, setuptools, and wheel are installed
RUN /root/.local/bin/pip install --no-cache-dir --upgrade pip setuptools wheel

# Copy project files
COPY pyproject.toml setup.py README.md LICENSE ./
COPY src ./src
COPY generated_kg ./generated_kg
COPY scripts ./scripts
COPY Script ./Script

# Set environment variables
ENV PATH=/root/.local/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Install the project in editable mode
RUN pip install --no-cache-dir -e .

# Default command
CMD ["python", "-m", "src.crewai.run"]
