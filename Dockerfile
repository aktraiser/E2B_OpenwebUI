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

# Create logs directory inside app directory
RUN mkdir -p /app/logs && \
    chmod 755 /app/logs

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Create non-root user and fix permissions
RUN useradd -m -u 1000 crewai && \
    chown -R crewai:crewai /app

USER crewai

EXPOSE 8000

# Start health endpoint and main application
CMD ["sh", "-c", "uvicorn healthcheck:app --host 0.0.0.0 --port 8000 & python main.py"]
