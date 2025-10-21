# Dockerfile for E2B CrewAI MCP Server
# Exposes MCP tools via HTTP REST API using mcpo

FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir mcpo uv

# Copy MCP server code
COPY mcp_server.py .
COPY crewai_agent.py .
COPY requirements.txt .

# Install additional dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port for HTTP API
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/docs || exit 1

# Start mcpo proxy server with our MCP server
# mcpo will expose MCP tools as REST API
CMD ["uvx", "mcpo", "--host", "0.0.0.0", "--port", "8000", "--", "python3", "mcp_server.py"]
