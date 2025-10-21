# Dockerfile for E2B CrewAI MCP Server
# Exposes MCP tools via HTTP REST API using mcpo

FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy files first
COPY mcp_server.py .
COPY api_server.py .
COPY requirements.txt .

# Install dependencies from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Expose port for HTTP API
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/docs || exit 1

# Start FastAPI server (exposes HTTP REST API for OpenWebUI)
CMD ["python3", "api_server.py"]
