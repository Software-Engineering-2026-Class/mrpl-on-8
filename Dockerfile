# Multi-stage build for Agentic AI Framework Generator
FROM python:3.11-slim as builder

WORKDIR /build

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies to a virtualenv
COPY requirements.txt .
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# Final stage
FROM python:3.11-slim

WORKDIR /app

# Install runtime system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user for running the app
RUN useradd -m -u 1000 appuser

# Copy Python virtualenv from builder
COPY --from=builder --chown=appuser:appuser /opt/venv /opt/venv

# Set up environment
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    VIRTUAL_ENV=/opt/venv

# Copy project files
COPY --chown=appuser:appuser pyproject.toml setup.py README.md LICENSE ./
COPY --chown=appuser:appuser src/crewai/ ./src/crewai/
COPY --chown=appuser:appuser generated_kg/CrewAI/ ./generated_kg/CrewAI/
COPY --chown=appuser:appuser scripts/ ./scripts/
COPY --chown=appuser:appuser Script/ ./Script/

# Install the project in editable mode
RUN pip install --no-cache-dir -e .

# Switch to non-root user
USER appuser

# Default command
CMD ["python", "-m", "src.crewai.run"]
