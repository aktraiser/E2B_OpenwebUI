#!/bin/bash

# Script pour configurer le MCP OpenAPI Server sur le VPS

echo "🚀 Configuration du MCP OpenAPI Server pour CSV Analyzer"

# 1. Installer le serveur MCP OpenAPI globalement
echo "📦 Installation du MCP OpenAPI Server..."
npm install -g @ivotoby/openapi-mcp-server

# 2. Créer le script de démarrage MCP
echo "📝 Création du script de démarrage..."
cat > /home/mcp-csv-analyzer.sh << 'EOF'
#!/bin/bash
npx @ivotoby/openapi-mcp-server \
  --api-base-url http://147.93.94.85:8091 \
  --openapi-spec http://147.93.94.85:8091/openapi.json \
  --name "csv-analyzer-e2b" \
  --server-version "2.0.0" \
  --transport stdio \
  --tools-mode all
EOF

chmod +x /home/mcp-csv-analyzer.sh

echo "✅ Configuration terminée !"
echo ""
echo "🔧 Pour utiliser dans OpenWebUI, ajoute cette configuration MCP :"
echo ""
echo '{
  "mcpServers": {
    "csv-analyzer": {
      "command": "/home/mcp-csv-analyzer.sh",
      "args": []
    }
  }
}'
echo ""
echo "🔗 URLs importantes :"
echo "- API REST : http://147.93.94.85:8091"
echo "- OpenAPI Spec : http://147.93.94.85:8091/openapi.json"
echo "- Swagger UI : http://147.93.94.85:8091/docs"