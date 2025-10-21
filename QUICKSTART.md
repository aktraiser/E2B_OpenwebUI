# 🚀 Quick Start - CrewAI + MCP dans E2B

## 📁 Structure du Projet

```
E2B/
├── api.py              # FastAPI server
├── crew.py             # Agent CrewAI
├── tools.py            # Tools MCP (HTTP vers localhost:8080)
├── requirements.txt    # Dépendances
├── README.md           # Documentation complète
├── ARCHITECTURE.md     # Schéma de l'architecture
└── DEPLOY.md           # Guide de déploiement détaillé
```

## ⚡ Démarrage Rapide

### 1. Créer le Template E2B

```python
from e2b import Template

template = (
    Template()
    .from_template("mcp-gateway")
    .beta_add_mcp_server(["duckduckgo", "arxiv"])
)

Template.build(template, alias="crewai-mcp")
```

### 2. Déployer depuis OpenWebUI

```python
from e2b import Sandbox

sbx = Sandbox.beta_create(
    template="crewai-mcp",
    mcp={"duckduckgo": {}, "arxiv": {}}
)

# Installer dépendances
sbx.commands.run("pip install -r requirements.txt")

# Lancer l'API
sbx.commands.run("uvicorn api:app --host 0.0.0.0 --port 8000 &")

# Obtenir l'URL
crew_url = sbx.get_host(8000)
print(f"API: {crew_url}")
```

### 3. Tester

```bash
curl -X POST http://<crew_url>/execute \
  -H "Content-Type: application/json" \
  -d '{"task": "Calculate 5 + 3 using Python"}'
```

## 🏗️ Architecture

```
E2B Sandbox
├── MCP Gateway (localhost:8080)
│   └── Tools: duckduckgo, arxiv
└── CrewAI (port 8000)
    └── HTTP calls → localhost:8080
```

## ✅ Points Clés

- ✅ Pas de `Sandbox.create()` dans les tools
- ✅ Tools font des appels HTTP vers MCP local
- ✅ Tout tourne dans le même sandbox

## 📚 Documentation

- `README.md` - Vue d'ensemble
- `ARCHITECTURE.md` - Détails techniques
- `DEPLOY.md` - Guide complet de déploiement

## 🎯 C'est Tout !

Le projet est prêt à déployer. Consultez `DEPLOY.md` pour les détails.
