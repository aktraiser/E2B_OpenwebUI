# Architecture E2B + MCP + CrewAI

## 🎯 Architecture Complète

```
OpenWebUI
    ↓ déploie
E2B Sandbox (avec template mcp-gateway)
├── MCP Gateway (localhost:8080)
│   ├── DuckDuckGo MCP server
│   ├── ArXiv MCP server
│   └── Autres MCP servers prepulled
│
└── CrewAI Application
    ├── FastAPI (port 8000)
    ├── Agent CrewAI
    └── Tools → HTTP calls vers localhost:8080/mcp
```

## 📝 Étapes de Déploiement

### 1. Créer le Template E2B (depuis local)

```python
from e2b import Template

# Créer template avec MCP servers prepulled
template = (
    Template()
    .from_template("mcp-gateway")
    .beta_add_mcp_server(["duckduckgo", "arxiv"])
)

Template.build(
    template,
    alias="crewai-mcp-template",
    cpu_count=4,
    memory_mb=4096,
)
```

### 2. Déployer depuis OpenWebUI

OpenWebUI va créer le sandbox:
```python
from e2b import Sandbox

sbx = Sandbox.beta_create(
    template="crewai-mcp-template",
    mcp={
        "duckduckgo": {},
        "arxiv": {"storagePath": "/"}
    }
)

# MCP Gateway démarre automatiquement sur localhost:8080
mcp_url = sbx.beta_get_mcp_url()  # URL interne: http://localhost:8080
```

### 3. Lancer CrewAI dans le Sandbox

```python
# Dans le sandbox, démarrer l'app CrewAI
sbx.commands.run("pip install -r requirements.txt")
sbx.commands.run("uvicorn api:app --host 0.0.0.0 --port 8000")

# Exposer le port
crew_url = sbx.get_host(8000)
print(f"CrewAI accessible sur: {crew_url}")
```

## 🔧 Code CrewAI (tools.py)

**IMPORTANT**: Ne PAS créer de nouveau sandbox, utiliser le MCP local !

```python
import requests
from crewai.tools import tool

MCP_URL = "http://localhost:8080"

@tool("Python Interpreter")
def execute_python(code: str) -> str:
    """Execute Python via MCP server"""
    response = requests.post(
        f"{MCP_URL}/tools/call",
        json={
            "name": "python_execution",  # Si MCP a ce tool
            "arguments": {"code": code}
        }
    )
    return response.json()

@tool("Search DuckDuckGo")
def search_duckduckgo(query: str) -> str:
    """Search via MCP DuckDuckGo"""
    response = requests.post(
        f"{MCP_URL}/tools/call",
        json={
            "name": "duckduckgo_search",
            "arguments": {"query": query}
        }
    )
    return response.json()
```

## ❌ Ce qu'il NE faut PAS faire

```python
# ❌ MAUVAIS - Crée un sandbox dans le sandbox
@tool("Python Interpreter")
def execute_python(code: str) -> str:
    with Sandbox.create() as sandbox:  # ❌ NON !
        execution = sandbox.run_code(code)
        return execution.text
```

## ✅ Ce qu'il faut faire

```python
# ✅ BON - Appelle le MCP local
@tool("Python Interpreter")
def execute_python(code: str) -> str:
    response = requests.post(
        "http://localhost:8080/tools/call",
        json={"name": "python_execution", "arguments": {"code": code}}
    )
    result = response.json()
    return result.get("content", [{}])[0].get("text", "")
```

## 🧪 Vérification

### Dans le sandbox, vérifier MCP tourne:
```bash
curl http://localhost:8080/tools/list
```

### Tester un tool MCP:
```bash
curl -X POST http://localhost:8080/tools/call \
  -H "Content-Type: application/json" \
  -d '{
    "name": "duckduckgo_search",
    "arguments": {"query": "test"}
  }'
```

## 📦 Structure Fichiers

```
/app/  (dans le sandbox)
├── api.py              # FastAPI server
├── crew.py             # Agent CrewAI
├── tools.py            # Tools → MCP local
├── requirements.txt    # Dépendances
└── .env               # Config
```

## 🚀 Workflow Complet

1. **Build template**: `Template.build(..., alias="crewai-mcp")`
2. **OpenWebUI crée sandbox**: `Sandbox.beta_create(template="crewai-mcp", mcp={...})`
3. **MCP Gateway démarre**: Automatique sur `localhost:8080`
4. **Installer CrewAI**: `pip install -r requirements.txt`
5. **Lancer API**: `uvicorn api:app --host 0.0.0.0 --port 8000`
6. **Tools utilisent MCP**: HTTP vers `localhost:8080`

## 💡 Points Clés

- ✅ Un seul sandbox E2B
- ✅ MCP Gateway tourne dedans (localhost:8080)
- ✅ CrewAI tourne dedans aussi (port 8000)
- ✅ Les tools font des HTTP calls vers localhost:8080
- ❌ Ne JAMAIS créer de nouveau sandbox dans les tools
