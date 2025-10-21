#!/bin/bash
# Start MCP Server on VPS
# Usage: ./start_mcp_server.sh

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Starting E2B CrewAI MCP Server...${NC}"

# Check if .env exists
if [ ! -f .env ]; then
    echo -e "${RED}❌ Error: .env file not found${NC}"
    echo "Please create a .env file with:"
    echo "  E2B_API_KEY=your_key"
    echo "  OPENAI_API_KEY=your_key"
    exit 1
fi

# Check if crewai_agent.py exists
if [ ! -f crewai_agent.py ]; then
    echo -e "${RED}❌ Error: crewai_agent.py not found${NC}"
    exit 1
fi

# Source environment variables
source .env

# Check required variables
if [ -z "$E2B_API_KEY" ] || [ -z "$OPENAI_API_KEY" ]; then
    echo -e "${RED}❌ Error: E2B_API_KEY and OPENAI_API_KEY must be set in .env${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Environment variables loaded${NC}"

# Install dependencies if needed
if ! python3 -c "import mcp" 2>/dev/null; then
    echo -e "${BLUE}📦 Installing dependencies...${NC}"
    pip install -q -r requirements.txt
fi

echo -e "${GREEN}✅ Dependencies ready${NC}"

# Start the MCP server
echo -e "${BLUE}🔌 Starting MCP server...${NC}"
echo -e "${GREEN}Ready to accept connections from OpenWebUI${NC}"
echo ""

python3 mcp_server.py
