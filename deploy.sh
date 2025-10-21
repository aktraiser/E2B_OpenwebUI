#!/bin/bash
set -e

echo "🚀 Deploying CrewAI E2B to VPS..."

# Check .env file
if [ ! -f ".env" ]; then
    echo "❌ .env file missing!"
    echo "💡 Copy .env.example to .env and add your API keys:"
    echo "   cp .env.example .env"
    exit 1
fi

# Validate API keys in .env
if ! grep -q "OPENAI_API_KEY=sk-" .env || ! grep -q "E2B_API_KEY=e2b_" .env; then
    echo "❌ Missing or invalid API keys in .env"
    echo "💡 Make sure to set valid OPENAI_API_KEY and E2B_API_KEY"
    exit 1
fi

# Stop existing services
echo "⏹️  Stopping existing services..."
docker-compose down 2>/dev/null || true

# Build Docker image
echo "🔨 Building Docker image..."
docker-compose build --no-cache

# Start services
echo "▶️  Starting services..."
docker-compose up -d

# Wait for health check
echo "⏳ Waiting for health check..."
sleep 10

# Check health
if curl -f http://localhost:8000/health 2>/dev/null; then
    echo ""
    echo "✅ Deployment successful!"
    echo ""
    echo "📊 Service Status:"
    echo "   Health: http://localhost:8000/health"
    echo "   Metrics: http://localhost:8000/metrics"
    echo ""
    echo "📝 View logs:"
    echo "   docker-compose logs -f crewai"
    echo ""
else
    echo ""
    echo "❌ Health check failed!"
    echo "📋 Checking logs..."
    docker-compose logs crewai
    exit 1
fi
