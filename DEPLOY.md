# 🚀 Guide de Déploiement - CrewAI + MCP dans E2B

## 📋 Checklist Avant Déploiement

- [ ] Template E2B créé avec MCP servers
- [ ] Fichier `tools.py` corrigé (pas de `Sandbox.create()`)
- [ ] `requirements.txt` à jour (inclut `requests`)
- [ ] Variables d'environnement configurées

## 🔧 Étape 1: Créer le Template E2B

**Sur votre machine locale** :

```python
from e2b import Template

# Créer template avec MCP Gateway + servers prepulled
template = (
    Template()
    .from_template("mcp-gateway")
    .beta_add_mcp_server(["duckduckgo", "arxiv"])
)

# Build le template
Template.build(
    template,
    alias="crewai-mcp",
    cpu_count=4,
    memory_mb=4096
)
```

## 📦 Étape 2: Préparer les Fichiers

### Fichiers requis:

```
/app/
├── api.py              # FastAPI server
├── crew.py             # Agent CrewAI
├── tools.py            # ← IMPORTANT: Utiliser tools_correct.py
├── requirements.txt    # Dépendances
└── .env               # Config (optionnel)
```

### Copier le bon fichier tools:

```bash
cp tools_correct.py tools.py
```

### Vérifier requirements.txt:

```txt
crewai>=0.28.0
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
requests>=2.31.0
pydantic>=2.0.0
```

## 🌐 Étape 3: Déployer depuis OpenWebUI

OpenWebUI va créer le sandbox avec votre template. Le code Python dans OpenWebUI:

```python
from e2b import Sandbox
import os

# Créer sandbox avec template
sbx = Sandbox.beta_create(
    template="crewai-mcp",  # Le template que vous avez créé
    mcp={
        "duckduckgo": {},
        "arxiv": {"storagePath": "/"}
    }
)

# MCP Gateway démarre automatiquement sur localhost:8080
mcp_url = sbx.beta_get_mcp_url()
print(f"MCP Gateway: {mcp_url}")

# Installer les dépendances
print("Installing dependencies...")
sbx.commands.run("pip install -r /app/requirements.txt")

# Lancer l'API CrewAI
print("Starting CrewAI API...")
sbx.commands.run("cd /app && uvicorn api:app --host 0.0.0.0 --port 8000 &")

# Attendre que le serveur démarre
import time
time.sleep(10)

# Obtenir l'URL publique
crew_url = sbx.get_host(8000)
print(f"CrewAI API accessible sur: {crew_url}")

# Garder le sandbox actif
# sbx.keep_alive(3600)  # 1 heure
```

## ✅ Étape 4: Vérification

### Test 1: Vérifier MCP Gateway

```bash
curl http://localhost:8080/tools/list
```

Devrait retourner la liste des tools MCP.

### Test 2: Vérifier CrewAI API

```bash
curl http://<crew_url>/health
```

### Test 3: Tester l'Exécution

```bash
curl -X POST http://<crew_url>/execute \
  -H "Content-Type: application/json" \
  -d '{"task": "Use execute_python tool to calculate 2 + 2"}'
```

Devrait maintenant **utiliser le tool** et retourner le résultat !

## 🐛 Troubleshooting

### "Connection refused to localhost:8080"

MCP Gateway pas démarré. Vérifier:
```bash
# Dans le sandbox
curl http://localhost:8080/health
```

Si erreur, vérifier que le template a bien `mcp-gateway` comme base.

### "Tool not found: python_execution"

Le MCP server n'a pas ce tool. Lister les tools disponibles:
```bash
curl -X POST http://localhost:8080/tools/list
```

Ajuster le nom du tool dans `tools.py` selon ce qui est disponible.

### "Timeout"

L'agent essaie toujours de créer un sandbox. Vérifier que `tools.py` utilise bien `requests.post()` et pas `Sandbox.create()`.

### Logs

Dans OpenWebUI, consulter les logs du sandbox:
```python
print(sbx.commands.run("tail -50 /var/log/app.log"))
```

## 📊 Architecture Déployée

```
OpenWebUI
    ↓ crée
E2B Sandbox (template: crewai-mcp)
├── MCP Gateway (localhost:8080)
│   ├── duckduckgo_search
│   └── arxiv_search
│
└── CrewAI App (port 8000)
    ├── FastAPI API
    ├── Agent CrewAI
    └── Tools → HTTP vers localhost:8080
        ↑
        │ HTTP depuis internet
        │
    OpenWebUI Tools Custom Templates
```

## 🎯 Résultat Attendu

Quand vous appelez l'API CrewAI:

1. L'agent reçoit la tâche
2. L'agent décide d'utiliser un tool (ex: `execute_python`)
3. Le tool fait un HTTP call vers `localhost:8080/tools/call`
4. Le MCP Gateway exécute le code
5. Le résultat est retourné à l'agent
6. L'agent formule la réponse finale

**Pas de timeout, pas d'erreur sandbox !**

## 📚 Fichiers de Référence

- `ARCHITECTURE.md` - Schéma complet
- `FIX_FINAL.md` - Explication de la correction
- `tools_correct.py` - Code corrigé des tools
- `README.md` - Documentation générale

## ✨ Prochaines Étapes

1. Tester avec des tâches simples
2. Ajouter plus de MCP servers si nécessaire
3. Configurer les timeouts selon vos besoins
4. Monitorer l'usage et les coûts E2B

---

**Important**: Le secret est que CrewAI et MCP tournent dans **le même sandbox**. Pas de création de sandbox imbriquée !
