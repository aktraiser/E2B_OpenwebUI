# 🌐 Configuration OpenWebUI avec E2B + CrewAI

## 📋 Architecture Complète

```
┌─────────────────────────────────────────┐
│         OpenWebUI (Interface)           │
│              avec LLM                    │
└────────────────┬────────────────────────┘
                 │ MCP Protocol
                 ↓
┌─────────────────────────────────────────┐
│    MCP Server (VPS: 147.93.94.85)       │
│    - execute_crewai_task                │
│    - list_sandboxes                     │
│    - cleanup_sandbox                    │
└────────────────┬────────────────────────┘
                 │ E2B SDK
                 ↓
┌─────────────────────────────────────────┐
│      E2B Sandbox (Cloud)                │
│  ┌──────────────────────────────────┐   │
│  │  MCP Gateway (localhost:8080)    │   │
│  │  - Browserbase                   │   │
│  │  - Exa                           │   │
│  │  - DuckDuckGo                    │   │
│  │  - ArXiv                         │   │
│  └──────────────────────────────────┘   │
│                                          │
│  ┌──────────────────────────────────┐   │
│  │  CrewAI Agent                    │   │
│  │  - Python Code Execution         │   │
│  │  - Web Search (via MCP)          │   │
│  │  - Research (via MCP)            │   │
│  └──────────────────────────────────┘   │
└─────────────────────────────────────────┘
```

## 🚀 Partie 1: Installation sur VPS

### Étape 1: Connexion au VPS

```bash
ssh root@147.93.94.85
```

### Étape 2: Créer le répertoire du projet

```bash
cd /root
mkdir e2b-crewai-mcp
cd e2b-crewai-mcp
```

### Étape 3: Upload des fichiers

**Option A: Via git**
```bash
git clone <votre-repo> .
```

**Option B: Via scp (depuis votre machine locale)**
```bash
scp mcp_server.py crewai_agent.py requirements.txt start_mcp_server.sh \
    root@147.93.94.85:/root/e2b-crewai-mcp/
```

### Étape 4: Créer le fichier .env

```bash
cat > .env << 'EOF'
# Obligatoire
E2B_API_KEY=e2b_xxx
OPENAI_API_KEY=sk-xxx

# Optionnel - MCP Servers
BROWSERBASE_API_KEY=
BROWSERBASE_PROJECT_ID=
GEMINI_API_KEY=
EXA_API_KEY=
EOF
```

**IMPORTANT:** Remplacez `e2b_xxx` et `sk-xxx` par vos vraies clés!

### Étape 5: Installer les dépendances

```bash
pip install -r requirements.txt
```

### Étape 6: Tester le serveur MCP

```bash
chmod +x start_mcp_server.sh
./start_mcp_server.sh
```

Si tout fonctionne, vous verrez:
```
🚀 Starting E2B CrewAI MCP Server...
✅ Environment variables loaded
✅ Dependencies ready
🔌 Starting MCP server...
Ready to accept connections from OpenWebUI
```

**Laissez ce terminal ouvert!** Le serveur MCP doit tourner en permanence.

### Étape 7: Démarrage automatique avec systemd (optionnel)

Pour que le serveur MCP démarre automatiquement:

```bash
cat > /etc/systemd/system/e2b-mcp.service << 'EOF'
[Unit]
Description=E2B CrewAI MCP Server
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/e2b-crewai-mcp
ExecStart=/root/e2b-crewai-mcp/start_mcp_server.sh
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Activer et démarrer le service
systemctl enable e2b-mcp
systemctl start e2b-mcp

# Vérifier le statut
systemctl status e2b-mcp

# Voir les logs
journalctl -u e2b-mcp -f
```

## 🌐 Partie 2: Configuration OpenWebUI

### Étape 1: Ajouter le MCP Server dans OpenWebUI

1. Ouvrir **OpenWebUI**
2. Aller dans **Settings** → **Tools** → **MCP Servers**
3. Cliquer sur **Add MCP Server**

### Étape 2: Configuration du serveur MCP

**Nom:** `E2B CrewAI`

**Commande:**

```bash
ssh root@147.93.94.85 'cd /root/e2b-crewai-mcp && python3 mcp_server.py'
```

**OU** si vous utilisez une connexion locale (si OpenWebUI tourne sur le même VPS):

```bash
cd /root/e2b-crewai-mcp && python3 mcp_server.py
```

**OU** via stdio (méthode recommandée):

```json
{
  "command": "ssh",
  "args": [
    "root@147.93.94.85",
    "cd /root/e2b-crewai-mcp && python3 mcp_server.py"
  ],
  "env": {}
}
```

### Étape 3: Configuration SSH sans mot de passe (si nécessaire)

Pour que OpenWebUI puisse se connecter au VPS sans demander de mot de passe:

```bash
# Sur la machine qui héberge OpenWebUI
ssh-keygen -t ed25519 -C "openwebui-mcp"
ssh-copy-id root@147.93.94.85

# Tester la connexion
ssh root@147.93.94.85 'echo "Connection OK"'
```

### Étape 4: Activer les outils dans OpenWebUI

1. Dans **Settings** → **Tools**
2. Vérifier que les outils suivants sont disponibles:
   - `execute_crewai_task`
   - `list_sandboxes`
   - `cleanup_sandbox`
3. Les activer tous

## 🧪 Partie 3: Test de l'Intégration

### Test 1: Vérifier que le MCP Server est connecté

Dans OpenWebUI, envoyer un message:

```
List available MCP tools
```

Le LLM devrait voir les 3 tools disponibles.

### Test 2: Exécuter une tâche simple

```
Use the execute_crewai_task tool to calculate how many r's are in the word "strawberry"
```

**Résultat attendu:**
```json
{
  "success": true,
  "result": "There are 3 r's in the word 'strawberry'...",
  "sandbox_id": "sbx_abc123"
}
```

### Test 3: Recherche web avec analyse

```
Use the execute_crewai_task tool to:
1. Search for the latest news about AI
2. Summarize the top 3 findings
```

L'agent CrewAI va:
1. Utiliser Browserbase ou DuckDuckGo pour chercher
2. Analyser les résultats
3. Retourner un résumé

### Test 4: Code Python complexe

```
Use the execute_crewai_task tool to:
Calculate the first 20 Fibonacci numbers and plot them as a chart
```

L'agent va:
1. Écrire du code Python
2. L'exécuter dans un sandbox E2B imbriqué
3. Retourner les résultats

## 🎯 Utilisation Pratique

### Exemple 1: Analyse de site web

**Prompt dans OpenWebUI:**
```
Analyze the website https://example.com and extract:
- Main topics discussed
- Key technical stack used
- Contact information

Use the execute_crewai_task tool.
```

### Exemple 2: Recherche académique

**Prompt:**
```
Search ArXiv for recent papers about "transformer neural networks"
and summarize the 3 most cited papers from 2024.

Use the execute_crewai_task tool.
```

### Exemple 3: Data analysis

**Prompt:**
```
Calculate and visualize:
1. Prime numbers up to 1000
2. Their distribution
3. Statistical analysis

Use the execute_crewai_task tool.
```

### Exemple 4: Réutiliser un sandbox (plus rapide)

**Premier appel:**
```
Use execute_crewai_task to search for AI news
```

Récupérer le `sandbox_id` dans la réponse (ex: `sbx_abc123`)

**Appels suivants:**
```
Use execute_crewai_task with sandbox_id "sbx_abc123" to analyze the previous results
```

Cela réutilise le même sandbox → **beaucoup plus rapide** (pas de setup)

## 🔧 Configuration Avancée

### Personnaliser les MCP Servers disponibles

Modifier [mcp_server.py:43-56](mcp_server.py#L43-L56):

```python
mcp={
    "browserbase": {...},
    "exa": {...},
    "github": {  # Ajouter GitHub
        "token": os.getenv("GITHUB_TOKEN")
    },
    "filesystem": {  # Ajouter accès fichiers
        "allowedPaths": ["/data"]
    }
}
```

### Modifier le modèle LLM utilisé par CrewAI

Dans [crewai_agent.py:95-98](crewai_agent.py#L95-L98):

```python
llm=LLM(
    model="gpt-4o-mini",  # Moins cher
    api_key=os.getenv("OPENAI_API_KEY")
)
```

Ou utiliser Claude:

```python
llm=LLM(
    model="claude-3-5-sonnet-20241022",
    api_key=os.getenv("ANTHROPIC_API_KEY")
)
```

### Augmenter les timeouts

Pour des tâches longues, modifier [mcp_server.py:167](mcp_server.py#L167):

```python
timeout=600000  # 10 minutes au lieu de 5
```

### Cache de sandboxes

Les sandboxes sont automatiquement mis en cache et réutilisés pendant 30 minutes.

Pour changer la durée: modifier [mcp_server.py:98](mcp_server.py#L98):

```python
sbx.keep_alive(3600)  # 1 heure au lieu de 30 min
```

## 🐛 Troubleshooting

### Erreur: "MCP Server connection refused"

**Cause:** Le serveur MCP ne tourne pas sur le VPS

**Solution:**
```bash
ssh root@147.93.94.85
cd /root/e2b-crewai-mcp
./start_mcp_server.sh
```

### Erreur: "Missing environment variables"

**Cause:** .env mal configuré

**Solution:**
```bash
ssh root@147.93.94.85
cd /root/e2b-crewai-mcp
cat .env  # Vérifier le contenu
```

### Erreur: "Task execution timeout"

**Cause:** La tâche prend trop de temps (>5 min par défaut)

**Solution:** Augmenter le timeout dans mcp_server.py ou simplifier la tâche

### Erreur: "Sandbox creation failed"

**Cause:**
- Quota E2B dépassé
- Clé API E2B invalide
- Problème réseau

**Solution:**
```bash
# Vérifier les sandboxes actifs
python3 << EOF
from e2b import Sandbox
sandboxes = Sandbox.list()
print(f"Active sandboxes: {len(sandboxes)}")
EOF
```

### Le LLM n'utilise pas les outils

**Cause:** Les outils ne sont pas activés dans OpenWebUI

**Solution:**
1. Settings → Tools
2. Vérifier que les outils MCP sont activés
3. Essayer un prompt plus explicite: "Use the execute_crewai_task tool to..."

### Logs du serveur MCP

```bash
# Si lancé via systemd
journalctl -u e2b-mcp -f

# Si lancé manuellement
# Les logs sont sur stdout
```

## 💰 Gestion des Coûts

### Coûts E2B

- **Sandbox principal:** ~$0.0001/seconde quand actif
- **Sandboxes imbriqués:** ~$0.0001/seconde par exécution de code

### Optimisations:

1. **Réutiliser les sandboxes** avec `sandbox_id`
2. **Limiter keep_alive** à 30 min
3. **Cleanup régulier:**
```
Use list_sandboxes to see active sandboxes
Use cleanup_sandbox with id "sbx_xxx" to remove old ones
```

### Coûts LLM

- **OpenWebUI LLM:** Selon votre config
- **CrewAI LLM (GPT-4o):** ~$0.005 par tâche en moyenne

## 📊 Monitoring

### Voir les sandboxes actifs

**Prompt dans OpenWebUI:**
```
Use list_sandboxes to show all active E2B sandboxes
```

### Dashboard E2B

https://e2b.dev/dashboard
- Usage en temps réel
- Coûts
- Sandboxes actifs

## 🎓 Ressources

- [Documentation E2B](https://e2b.dev/docs)
- [CrewAI Documentation](https://docs.crewai.com)
- [MCP Protocol](https://modelcontextprotocol.io)
- [OpenWebUI MCP Guide](https://docs.openwebui.com/features/mcp)

---

**Prêt à démarrer!** 🚀

Si vous avez des questions, consultez la section Troubleshooting ou ouvrez une issue.
