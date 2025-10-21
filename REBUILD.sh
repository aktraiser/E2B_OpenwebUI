#!/bin/bash
# Quick rebuild script

echo "🔄 Rebuilding E2B CrewAI Docker container..."

# Stop and remove old container
docker-compose down

# Rebuild with no cache
docker-compose build --no-cache

# Start container
docker-compose up -d

echo ""
echo "✅ Container rebuilt!"
echo ""
echo "📊 Checking logs..."
docker-compose logs --tail=50 -f
