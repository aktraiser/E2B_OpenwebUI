# 🤖 E2B + CrewAI + MCP pour OpenWebUI

Système complet d'agents AI avec exécution de code sécurisée et outils de recherche via MCP.

## 📋 Vue d'Ensemble

Ce projet permet à **OpenWebUI** d'utiliser des **agents CrewAI** tournant dans des **sandboxes E2B** avec accès à des **outils MCP** (recherche web, exécution de code, etc.).

### Architecture en 3 niveaux:

```
OpenWebUI (Interface + LLM)
    ↓ MCP Protocol
MCP Server (VPS: 147.93.94.85)
    ↓ E2B SDK
E2B Sandbox (MCP Gateway + CrewAI Agent)
```

## ✨ Fonctionnalités

- 🐍 **Exécution de code Python** sécurisée via E2B Code Interpreter
- 🔍 **Recherche web** via Browserbase, DuckDuckGo, Exa
- 📚 **Recherche académique** via ArXiv
- 🤖 **Agents CrewAI** avec raisonnement multi-étapes
- ♻️ **Réutilisation de sandboxes** pour performance optimale
- 🔒 **Isolation complète** - code exécuté dans le cloud

## 🚀 Quick Start (Méthode Recommandée: Docker)

### 1. Déploiement sur VPS avec Docker

```bash
# Connexion au VPS
ssh root@147.93.94.85

# Clone du projet
cd /root
git clone <repo> e2b-crewai-mcp
cd e2b-crewai-mcp

# Configuration des clés API
cat > .env << 'EOF'
E2B_API_KEY=your_e2b_key
OPENAI_API_KEY=your_openai_key
EOF

# Démarrage avec Docker Compose
docker-compose up -d

# Vérifier que ça tourne
docker-compose logs -f
```

### 2. Configuration OpenWebUI

1. **Settings** → **Functions** → **+ Add Function**
2. Ajouter une **OpenAPI Function**:
   - **OpenAPI URL**: `http://147.93.94.85:8000/openapi.json`
   - Ou visiter: `http://147.93.94.85:8000/docs` et importer depuis Swagger
3. **Activer la fonction**

### 3. Test

Dans OpenWebUI:

```
Use the execute_crewai_task function to calculate the first 10 Fibonacci numbers
```

### 📖 Guide Complet

Voir [DOCKER_DEPLOY.md](DOCKER_DEPLOY.md) pour le guide de déploiement Docker complet.

---

## 🔄 Alternative: Déploiement sans Docker

Pour déploiement direct (sans Docker), voir [OPENWEBUI_SETUP.md](OPENWEBUI_SETUP.md).

## 📦 Structure du Projet

```
.
├── Dockerfile              # 🐳 Image Docker
├── docker-compose.yml      # 🐳 Orchestration Docker
├── mcp_server.py           # ⚙️ Serveur MCP
├── crewai_agent.py         # 🤖 Agent CrewAI (E2B)
├── requirements.txt        # 📦 Dépendances Python
├── start_mcp_server.sh     # 🚀 Script démarrage (sans Docker)
├── .env                    # 🔑 Configuration (à créer)
│
├── README.md               # 📖 Ce fichier
├── DOCKER_DEPLOY.md        # 📖 Guide Docker (recommandé)
├── OPENWEBUI_SETUP.md      # 📖 Guide OpenWebUI (sans Docker)
└── VPS_DEPLOY_GUIDE.md     # 📖 Tests manuels
```

## 🔧 Fichiers Clés

### [mcp_server.py](mcp_server.py)

Serveur MCP qui tourne sur le VPS et expose 3 outils à OpenWebUI:

- `execute_crewai_task` - Exécuter une tâche avec CrewAI
- `list_sandboxes` - Lister les sandboxes actifs
- `cleanup_sandbox` - Nettoyer un sandbox

### [crewai_agent.py](crewai_agent.py)

Agent CrewAI qui tourne dans le sandbox E2B avec:

- **Tool 1:** `execute_python` - Exécution de code Python
- **Tool 2:** `search_web` - Recherche web via MCP

### [start_mcp_server.sh](start_mcp_server.sh)

Script bash pour démarrer le serveur MCP avec vérifications

## 🎯 Cas d'Usage

### 1. Analyse de données

```
Analyze this dataset and create visualizations:
[1, 5, 3, 8, 2, 9, 4, 7, 6]

Use the execute_crewai_task tool.
```

### 2. Recherche + Synthèse

```
Research the latest developments in quantum computing
and summarize the top 3 breakthroughs from 2024.

Use the execute_crewai_task tool.
```

### 3. Web Scraping + Analyse

```
Analyze the website https://news.ycombinator.com
and extract the top 5 trending topics.

Use the execute_crewai_task tool.
```

## ⚙️ Configuration

### Variables d'Environnement Requises

```bash
# Obligatoire
E2B_API_KEY=e2b_xxx           # https://e2b.dev
OPENAI_API_KEY=sk-xxx         # https://platform.openai.com

# Optionnel - MCP Servers
BROWSERBASE_API_KEY=          # https://browserbase.com
BROWSERBASE_PROJECT_ID=
GEMINI_API_KEY=               # Pour Browserbase
EXA_API_KEY=                  # https://exa.ai
```

## 🐛 Troubleshooting

| Erreur | Cause | Solution |
|--------|-------|----------|
| "MCP Server connection refused" | Serveur pas démarré | `ssh root@147.93.94.85 './start_mcp_server.sh'` |
| "Missing environment variables" | .env mal configuré | Vérifier E2B_API_KEY et OPENAI_API_KEY |
| "Sandbox creation failed" | Quota E2B dépassé | Vérifier dashboard E2B |
| "Task timeout" | Tâche trop longue | Augmenter timeout dans mcp_server.py |

Voir [OPENWEBUI_SETUP.md](OPENWEBUI_SETUP.md) pour plus de détails.

## 💰 Coûts

### E2B
- Sandbox principal: ~$0.0001/seconde
- Sandboxes code: ~$0.0001/seconde par exécution
- **Optimisation:** Réutiliser les sandboxes avec `sandbox_id`

### OpenAI
- GPT-4o: ~$0.005 par tâche CrewAI en moyenne
- **Optimisation:** Utiliser GPT-4o-mini

## 📚 Documentation

- **[DOCKER_DEPLOY.md](DOCKER_DEPLOY.md)** - 🐳 Guide de déploiement Docker (RECOMMANDÉ)
- **[OPENWEBUI_SETUP.md](OPENWEBUI_SETUP.md)** - Guide OpenWebUI sans Docker + troubleshooting
- **[VPS_DEPLOY_GUIDE.md](VPS_DEPLOY_GUIDE.md)** - Déploiement et tests manuels
- **[E2B Docs](https://e2b.dev/docs)** - Documentation E2B
- **[CrewAI Docs](https://docs.crewai.com)** - Documentation CrewAI
- **[MCP Docs](https://modelcontextprotocol.io)** - Protocole MCP
- **[mcpo GitHub](https://github.com/modelcontextprotocol/mcpo)** - MCP-to-OpenAPI proxy

---

**Questions?** Voir [DOCKER_DEPLOY.md](DOCKER_DEPLOY.md) ou ouvrir une issue.
