FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y curl && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code and config
COPY *.py ./
COPY config/ ./config/

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Create non-root user and create logs directory with proper permissions
RUN useradd -m -u 1000 crewai && \
    mkdir -p /app/logs && \
    chown -R crewai:crewai /app && \
    chmod 755 /app/logs

USER crewai

EXPOSE 8000

# Start API server with both health and task execution endpoints
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
