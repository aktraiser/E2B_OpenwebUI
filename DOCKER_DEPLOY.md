# 🐳 Déploiement Docker - E2B CrewAI MCP Server

Guide pour déployer le serveur MCP via Docker avec exposition HTTP/REST pour OpenWebUI.

## 🏗️ Architecture

```
OpenWebUI (Interface)
    ↓ HTTP REST API
Docker Container (VPS: 147.93.94.85:8000)
├── mcpo (MCP-to-OpenAPI proxy)
│   ├── Expose: http://147.93.94.85:8000/docs
│   └── Tools: execute_crewai_task, list_sandboxes, cleanup_sandbox
│
└── mcp_server.py
    ↓ E2B SDK
    E2B Sandbox (Cloud)
    ├── MCP Gateway
    └── CrewAI Agent
```

## ✨ Avantages de cette approche

✅ **HTTP REST API** - Facile à intégrer dans OpenWebUI
✅ **Documentation auto** - Swagger UI sur `/docs`
✅ **Docker** - Déploiement simple et reproductible
✅ **Pas de SSH** - OpenWebUI appelle juste une URL HTTP
✅ **Sécurisé** - Peut ajouter HTTPS facilement

## 🚀 Quick Start

### 1. Sur le VPS

```bash
# Connexion
ssh root@147.93.94.85

# Cloner le projet
cd /root
git clone <votre-repo> e2b-crewai-mcp
cd e2b-crewai-mcp

# Créer le fichier .env
cat > .env << 'EOF'
E2B_API_KEY=e2b_xxx
OPENAI_API_KEY=sk-xxx

# Optionnel
BROWSERBASE_API_KEY=
BROWSERBASE_PROJECT_ID=
GEMINI_API_KEY=
EXA_API_KEY=
EOF

# Démarrer avec Docker Compose
docker-compose up -d

# Vérifier les logs
docker-compose logs -f
```

### 2. Vérifier que ça tourne

```bash
# Check health
curl http://147.93.94.85:8000/docs

# Devrait retourner la page Swagger UI
```

### 3. Configurer OpenWebUI

Dans **OpenWebUI**:

1. Aller dans **Settings** → **Functions** → **+ Add Function**
2. Ajouter une **OpenAPI Function**:
   - **Name**: `E2B CrewAI`
   - **OpenAPI URL**: `http://147.93.94.85:8000/openapi.json`
   - Ou importer directement depuis: `http://147.93.94.85:8000/docs`

3. Activer la fonction

### 4. Test

Dans OpenWebUI, envoyer:

```
Use the execute_crewai_task function to calculate fibonacci numbers up to 20
```

## 📦 Fichiers du Projet

### [Dockerfile](Dockerfile)

```dockerfile
FROM python:3.11-slim
WORKDIR /app

# Install mcpo (MCP-to-OpenAPI proxy)
RUN pip install mcpo uv

# Copy application files
COPY mcp_server.py crewai_agent.py requirements.txt .

# Install dependencies
RUN pip install -r requirements.txt

# Expose HTTP port
EXPOSE 8000

# Start mcpo proxy
CMD ["uvx", "mcpo", "--host", "0.0.0.0", "--port", "8000", "--", "python3", "mcp_server.py"]
```

### [docker-compose.yml](docker-compose.yml)

```yaml
version: '3.8'

services:
  e2b-mcp-server:
    build: .
    ports:
      - "8000:8000"
    env_file:
      - .env
    restart: unless-stopped
```

## 🔧 Commandes Docker

### Démarrer le serveur

```bash
docker-compose up -d
```

### Arrêter le serveur

```bash
docker-compose down
```

### Voir les logs

```bash
# Logs en temps réel
docker-compose logs -f

# Logs des dernières 100 lignes
docker-compose logs --tail=100
```

### Rebuild après modification du code

```bash
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Entrer dans le container

```bash
docker exec -it e2b-crewai-mcp bash
```

## 🌐 Accès aux APIs

Une fois déployé, les endpoints sont disponibles:

### Documentation Interactive

```
http://147.93.94.85:8000/docs
```

Page Swagger UI avec tous les endpoints disponibles.

### OpenAPI Schema

```
http://147.93.94.85:8000/openapi.json
```

Schéma OpenAPI pour import dans OpenWebUI.

### Endpoints REST

- `POST /execute_crewai_task` - Exécuter une tâche
- `GET /list_sandboxes` - Lister les sandboxes
- `DELETE /cleanup_sandbox/{sandbox_id}` - Nettoyer un sandbox

## 🧪 Test Manuel des APIs

### Test avec curl

```bash
# Exécuter une tâche
curl -X POST http://147.93.94.85:8000/execute_crewai_task \
  -H "Content-Type: application/json" \
  -d '{
    "task": "Calculate how many r'\''s are in '\''strawberry'\''"
  }'

# Lister les sandboxes
curl http://147.93.94.85:8000/list_sandboxes

# Nettoyer un sandbox
curl -X DELETE http://147.93.94.85:8000/cleanup_sandbox/sbx_abc123
```

### Test avec Python

```python
import requests

# Exécuter une tâche
response = requests.post(
    "http://147.93.94.85:8000/execute_crewai_task",
    json={"task": "Calculate fibonacci numbers up to 20"}
)

print(response.json())
```

## 🔒 Sécurité (Production)

### Ajouter HTTPS avec nginx reverse proxy

```nginx
# /etc/nginx/sites-available/e2b-mcp
server {
    listen 80;
    server_name mcp.yourdomain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

Puis activer Let's Encrypt:

```bash
certbot --nginx -d mcp.yourdomain.com
```

### Ajouter Authentication

Modifier `mcp_server.py` pour ajouter API key validation:

```python
from fastapi import Header, HTTPException

async def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != os.getenv("API_KEY"):
        raise HTTPException(status_code=403, detail="Invalid API Key")
    return x_api_key

@app.call_tool(dependencies=[Depends(verify_api_key)])
async def call_tool(name: str, arguments: Any):
    ...
```

## 🐛 Troubleshooting

### Container ne démarre pas

```bash
# Vérifier les logs
docker-compose logs

# Vérifier les variables d'environnement
docker-compose exec e2b-mcp-server env | grep -E "E2B|OPENAI"
```

### Port 8000 déjà utilisé

```bash
# Changer le port dans docker-compose.yml
ports:
  - "8080:8000"  # Utilise 8080 sur le host
```

### Erreur "Missing environment variables"

```bash
# Vérifier que .env existe et contient les clés
cat .env

# Rebuild le container
docker-compose down
docker-compose up -d
```

### mcpo ne trouve pas mcp_server.py

```bash
# Vérifier que les fichiers sont bien copiés
docker-compose exec e2b-mcp-server ls -la /app
```

## 📊 Monitoring

### Health check

```bash
# Vérifier la santé du container
docker ps

# Devrait montrer "healthy"
```

### Logs en temps réel

```bash
docker-compose logs -f
```

### Ressources utilisées

```bash
docker stats e2b-crewai-mcp
```

## 🔄 Mise à Jour

```bash
# Pull les dernières modifications
git pull

# Rebuild et redémarrer
docker-compose down
docker-compose build
docker-compose up -d
```

## 💰 Coûts

Même architecture E2B que précédemment:

- **Container Docker**: Gratuit (tourne sur votre VPS)
- **E2B Sandboxes**: ~$0.0001/seconde
- **OpenAI GPT-4o**: ~$0.005 par tâche

## 📚 Ressources

- [mcpo GitHub](https://github.com/modelcontextprotocol/mcpo)
- [OpenWebUI MCP Docs](https://docs.openwebui.com/features/mcp)
- [E2B Documentation](https://e2b.dev/docs)
- [Docker Compose Docs](https://docs.docker.com/compose/)

## 🎯 Prochaines Étapes

1. ✅ Déployer avec Docker Compose
2. ✅ Configurer dans OpenWebUI
3. ⏳ (Optionnel) Ajouter HTTPS avec nginx
4. ⏳ (Optionnel) Ajouter authentication
5. ⏳ (Optionnel) Setup monitoring avec Prometheus

---

**Questions?** Consulter les logs ou ouvrir une issue sur GitHub.
