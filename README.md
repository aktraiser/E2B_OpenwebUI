# CrewAI + MCP dans E2B Sandbox

Architecture: **CrewAI et MCP tournent ensemble dans le même sandbox E2B**

## 🏗️ Architecture

```
E2B Sandbox (créé via AsyncSandbox.beta_create)
├── MCP Server (écoute sur localhost:8080)
│   ├── Tool: duckduckgo_search
│   ├── Tool: arxiv_search
│   └── Tool: python_execution
│
└── CrewAI API (écoute sur 0.0.0.0:8000)
    ├── FastAPI server (api.py)
    ├── CrewAI Agent (crew.py)
    └── Tools MCP (tools.py)
         └── HTTP calls → localhost:8080
```

## 📝 Comment ça fonctionne

1. **Un sandbox E2B unique** est créé avec `AsyncSandbox.beta_create(mcp={...})`
2. **Le MCP server démarre automatiquement** dans le sandbox sur `localhost:8080`
3. **CrewAI tourne dans le même sandbox** et expose une API sur port `8000`
4. **Les tools CrewAI** font des requêtes HTTP vers `localhost:8080` pour utiliser les MCP tools

## 🔧 Fichiers

### `tools.py` - Tools CrewAI → MCP
```python
# Appelle le MCP server via HTTP
def call_mcp_tool(tool_name, arguments):
    requests.post("http://localhost:8080/tools/call", ...)
```

### `crew.py` - Agent CrewAI
```python
# Définit l'agent avec les tools MCP
agent = Agent(
    tools=[execute_python, search_duckduckgo, ...],
    ...
)
```

### `api.py` - FastAPI Server
```python
# Expose l'agent CrewAI via HTTP
@app.post("/execute")
def execute_task(request):
    crew = create_crew(request.task)
    return crew.kickoff()
```

## 🚀 Déploiement

### 1. Configuration

Créer `.env`:
```bash
OPENAI_API_KEY=sk-...
E2B_API_KEY=e2b_...
MCP_URL=http://localhost:8080  # MCP server local
```

### 2. Créer le Sandbox

Le sandbox est créé par votre code Python avec:
```python
sandbox = await AsyncSandbox.beta_create(
    mcp={
        "duckduckgo": {},
        "arxiv": {"storagePath": "/"}
    }
)
```

Cela démarre automatiquement le MCP server.

### 3. Lancer CrewAI dans le sandbox

```python
# Dans le sandbox, lancer l'API CrewAI
await sandbox.commands.run("uvicorn api:app --host 0.0.0.0 --port 8000")
```

### 4. Exposer le port

```python
# Obtenir l'URL publique
url = sandbox.get_host(8000)
print(f"CrewAI API: {url}")
```

## 🧪 Test

### Test local des tools

```bash
# Tester l'exécution Python
curl -X POST http://localhost:8000/execute \
  -H "Content-Type: application/json" \
  -d '{"task": "Use execute_python to calculate 5 + 3"}'
```

### Vérifier MCP server

```bash
# Lister les tools MCP disponibles
curl -X POST http://localhost:8080/tools/list
```

## 📊 Variables d'environnement

| Variable | Description | Défaut |
|----------|-------------|---------|
| `MCP_URL` | URL du MCP server | `http://localhost:8080` |
| `MCP_TOKEN` | Token d'auth MCP (optionnel) | `` |
| `OPENAI_API_KEY` | Clé API OpenAI | Requis |
| `E2B_API_KEY` | Clé API E2B | Requis |

## 🐛 Debugging

### Vérifier que MCP tourne

```bash
# Dans le sandbox
curl http://localhost:8080/health
```

### Vérifier les tools MCP

```bash
curl -X POST http://localhost:8080/tools/list
```

### Logs CrewAI

```python
# Activer verbose dans crew.py
agent = Agent(..., verbose=True)
crew = Crew(..., verbose=True)
```

## ⚠️ Erreurs Communes

### "MCP call failed: Connection refused"
→ Le MCP server n'est pas démarré dans le sandbox

### "Timeout"
→ MCP_URL incorrect ou firewall bloque localhost

### "Tool not found"
→ Le MCP server n'a pas été créé avec les bons MCP servers

## 🎯 Prochaines Étapes

1. ✅ Tools simplifiés (HTTP vers MCP local)
2. ✅ Pas de création de sandbox imbriquée
3. ⏳ Tester le déploiement complet
4. ⏳ Vérifier que l'agent utilise les tools

## 📚 Références

- [E2B MCP Beta](https://e2b.dev/docs/mcp)
- [CrewAI Tools](https://docs.crewai.com/tools)
- [MCP Protocol](https://modelcontextprotocol.io/)
