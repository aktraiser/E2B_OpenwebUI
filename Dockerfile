FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y curl && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY *.py ./

# Create logs directory
RUN mkdir -p /var/log/crewai && \
    chmod 755 /var/log/crewai

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Create non-root user
RUN useradd -m -u 1000 crewai && \
    chown -R crewai:crewai /app /var/log/crewai

USER crewai

EXPOSE 8000

# Start health endpoint and main application
CMD ["sh", "-c", "uvicorn healthcheck:app --host 0.0.0.0 --port 8000 & python main.py"]
