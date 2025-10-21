# 🚀 Guide de Déploiement VPS - CrewAI + E2B MCP

## 📋 Architecture

```
VPS (root@147.93.94.85)
    │
    ├── deploy_vps.py (script de déploiement)
    ├── crewai_agent.py (code CrewAI)
    └── .env (clés API)

    ↓ Crée via E2B SDK

E2B Sandbox Principal
    ├── MCP Gateway (localhost:8080)
    │   ├── Browserbase MCP Server
    │   └── Exa MCP Server
    │
    └── CrewAI Agent (process Python)
        ├── LLM: GPT-4o
        └── Tools:
            ├── execute_python → E2B Code Interpreter (sandbox imbriqué)
            └── search_web → MCP Gateway (localhost:8080)
```

## 🔑 Prérequis

### Clés API nécessaires:

1. **E2B_API_KEY** - Obligatoire
   - Obtenir sur: https://e2b.dev/dashboard

2. **OPENAI_API_KEY** - Obligatoire
   - Pour le LLM GPT-4o utilisé par CrewAI

3. **Clés MCP optionnelles** (selon les outils voulus):
   - BROWSERBASE_API_KEY
   - BROWSERBASE_PROJECT_ID
   - GEMINI_API_KEY (pour Browserbase)
   - EXA_API_KEY

## 📦 Installation sur VPS

### Étape 1: Connexion au VPS

```bash
ssh root@147.93.94.85
```

### Étape 2: Cloner le projet

```bash
cd /root
git clone <votre-repo> crewai-e2b
cd crewai-e2b
```

Ou upload les fichiers:
```bash
# Sur votre machine locale
scp crewai_agent.py deploy_vps.py requirements_vps.txt root@147.93.94.85:/root/crewai-e2b/
```

### Étape 3: Créer le fichier .env

```bash
cat > .env << 'EOF'
# Obligatoire
E2B_API_KEY=your_e2b_api_key_here
OPENAI_API_KEY=your_openai_api_key_here

# Optionnel - MCP Servers
BROWSERBASE_API_KEY=your_browserbase_key
BROWSERBASE_PROJECT_ID=your_project_id
GEMINI_API_KEY=your_gemini_key
EXA_API_KEY=your_exa_key
EOF
```

### Étape 4: Installer les dépendances VPS

```bash
pip install -r requirements_vps.txt
```

## 🚀 Déploiement

### Lancer le déploiement:

```bash
python deploy_vps.py
```

### Ce que fait le script:

1. ✅ Crée un sandbox E2B avec MCP Gateway
2. 📤 Upload le code CrewAI dans le sandbox
3. 📦 Installe les dépendances dans le sandbox
4. 🧪 Teste le MCP Gateway
5. 🤖 Exécute l'agent CrewAI
6. ⏱️ Garde le sandbox actif pendant 1h

### Résultat attendu:

```
🚀 Creating E2B sandbox with MCP Gateway...
✅ Sandbox created: sbx_abc123xyz
📡 MCP Gateway URL: https://...e2b.dev
📤 Uploading CrewAI agent code...
🔧 Configuring environment...
📦 Installing dependencies...
🧪 Testing MCP Gateway...
Available MCP tools: [...]

🤖 Running CrewAI agent...
============================================================
CREWAI RESULT:
============================================================
[Agent execution output with tool usage]

✅ Deployment complete!
```

## 🧪 Test Manuel

### Se connecter au sandbox:

```python
from e2b import Sandbox

# Utiliser l'ID affiché lors du déploiement
sbx = Sandbox.connect('sbx_abc123xyz')

# Tester MCP Gateway
result = sbx.commands.run("curl http://localhost:8080/tools/list")
print(result.stdout)

# Exécuter l'agent
result = sbx.commands.run(
    "bash -c 'source /root/.env_setup && python /root/crewai_agent.py'"
)
print(result.stdout)
```

### Tester un outil spécifique:

```python
# Modifier crewai_agent.py pour une tâche personnalisée
crew = create_crew("Search for the latest AI research papers about transformers")
result = crew.kickoff()
print(result)
```

## 🔧 Personnalisation

### Ajouter des MCP Servers:

Modifier [deploy_vps.py](deploy_vps.py:20-30):

```python
mcp={
    "browserbase": {...},
    "exa": {...},
    "github": {  # Nouveau serveur
        "token": os.getenv("GITHUB_TOKEN")
    }
}
```

### Ajouter des Tools CrewAI:

Modifier [crewai_agent.py](crewai_agent.py:50-80):

```python
@tool("GitHub Search")
def search_github(query: str) -> str:
    """Search GitHub repos via MCP"""
    response = requests.post(
        "http://localhost:8080/tools/call",
        json={"name": "github_search", "arguments": {"query": query}}
    )
    return response.json()
```

### Modifier le modèle LLM:

Dans [crewai_agent.py](crewai_agent.py:95-98):

```python
llm=LLM(
    model="gpt-4o-mini",  # Moins cher
    # ou
    model="claude-3-5-sonnet-20241022",  # Anthropic
    api_key=os.getenv("ANTHROPIC_API_KEY")
)
```

## 🐛 Troubleshooting

### Erreur: "Agent refuses to use tools"

**Cause**: Backstory trop restrictif

**Solution**: Vérifier que le backstory dans [crewai_agent.py](crewai_agent.py:87-93) dit explicitement d'utiliser les outils:

```python
backstory="""You ALWAYS use tools when needed..."""
```

### Erreur: "Connection to localhost:8080 refused"

**Cause**: MCP Gateway pas démarré

**Solution**:
```python
# Vérifier les logs du sandbox
sbx = Sandbox.connect('sbx_id')
logs = sbx.commands.run("ps aux | grep mcp")
print(logs.stdout)
```

### Erreur: "Timeout when creating nested sandbox"

**Cause**: Trop de sandboxes imbriqués ou quota dépassé

**Solution**:
- Vérifier quota E2B sur le dashboard
- Limiter le nombre d'appels simultanés à `execute_python`

### Erreur: "Module not found: crewai"

**Cause**: Dépendances pas installées dans le sandbox

**Solution**: Vérifier que requirements.txt est bien uploadé et pip install réussit

```python
result = sbx.commands.run("pip list | grep crewai")
print(result.stdout)
```

## 💰 Gestion des Coûts

### Sandboxes E2B:

- Sandbox principal: Actif tant que `keep_alive()` est appelé
- Sandboxes imbriqués (code execution): Créés/détruits à chaque appel de `execute_python`

### Optimisations:

1. **Limiter la durée de vie**:
```python
sandbox.keep_alive(1800)  # 30 min au lieu de 1h
```

2. **Réutiliser le sandbox**:
```python
# Garder l'ID et se reconnecter
SANDBOX_ID = "sbx_abc123"
sbx = Sandbox.connect(SANDBOX_ID)
```

3. **Pooling pour code execution**:
```python
# Dans crewai_agent.py - créer un pool de sandboxes
_sandbox_pool = []

def get_sandbox():
    if _sandbox_pool:
        return _sandbox_pool.pop()
    return Sandbox.create()

def return_sandbox(sbx):
    _sandbox_pool.append(sbx)
```

## 📊 Monitoring

### Voir les sandboxes actifs:

```python
from e2b import Sandbox

sandboxes = Sandbox.list()
for sbx in sandboxes:
    print(f"ID: {sbx.id}, Created: {sbx.created_at}")
```

### Logs d'exécution:

```python
sbx = Sandbox.connect('sbx_id')
logs = sbx.commands.run("tail -100 /var/log/syslog")
print(logs.stdout)
```

## 🎯 Utilisation en Production

### 1. API REST autour de CrewAI:

Créer [api.py](api.py) dans le sandbox:

```python
from fastapi import FastAPI
from crewai_agent import create_crew

app = FastAPI()

@app.post("/execute")
def execute_task(task: str):
    crew = create_crew(task)
    result = crew.kickoff()
    return {"result": str(result)}
```

Puis dans [deploy_vps.py](deploy_vps.py):
```python
# Lancer l'API
sbx.commands.run(
    "bash -c 'source /root/.env_setup && uvicorn api:app --host 0.0.0.0 --port 8000 &'"
)

# Obtenir l'URL publique
api_url = sbx.get_host(8000)
print(f"API accessible sur: {api_url}")
```

### 2. Intégration avec OpenWebUI:

Dans OpenWebUI, créer un Custom Function qui appelle votre API E2B.

## 📚 Fichiers du Projet

- [crewai_agent.py](crewai_agent.py) - Agent CrewAI avec tools
- [deploy_vps.py](deploy_vps.py) - Script de déploiement
- [requirements_vps.txt](requirements_vps.txt) - Dépendances VPS
- `.env` - Clés API (à créer)

## 🔗 Ressources

- [E2B Documentation](https://e2b.dev/docs)
- [CrewAI Documentation](https://docs.crewai.com)
- [MCP Protocol](https://modelcontextprotocol.io)
- [E2B MCP Guide](https://e2b.dev/docs/mcp)

---

**Questions?** Ouvrir une issue sur GitHub ou consulter les docs E2B.
