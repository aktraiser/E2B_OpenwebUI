# CSV Analyzer MCP Server - Déploiement VPS

Ce projet contient un serveur MCP (Model Context Protocol) pour l'analyse de fichiers CSV avec E2B Code Interpreter, intégrable avec OpenWebUI.

## Architecture

- **Serveur MCP natif** : `mcp_server.py` utilisant FastMCP
- **Protocole** : JSON-RPC via stdio pour communication avec OpenWebUI
- **Sandbox** : E2B Code Interpreter pour exécution sécurisée
- **Visualisations** : Matplotlib/Seaborn avec export PNG

## Outils MCP Disponibles

1. **analyze_csv_from_url** : Analyse CSV depuis URL publique
2. **analyze_csv_from_content** : Analyse CSV depuis contenu texte

## Déploiement sur VPS

### Option 1 : Déploiement Direct (Recommandé)

```bash
# 1. Transférer les fichiers sur le VPS
scp -r . user@147.93.94.85:/tmp/csv-analyzer-mcp/

# 2. Se connecter au VPS
ssh user@147.93.94.85

# 3. Exécuter le script de déploiement
cd /tmp/csv-analyzer-mcp
sudo ./deploy-mcp-server.sh

# 4. Configurer la clé API E2B
sudo nano /opt/csv-analyzer-mcp/.env
# Modifier: E2B_API_KEY=votre_vraie_cle_ici

# 5. Redémarrer le service
sudo systemctl restart csv-analyzer-mcp
```

### Option 2 : Déploiement Docker

```bash
# Sur le VPS
docker build -t csv-analyzer-mcp .
docker run -d --name csv-analyzer-mcp \
  -e E2B_API_KEY=votre_cle_api \
  --restart unless-stopped \
  csv-analyzer-mcp
```

## Configuration OpenWebUI

Ajouter dans les paramètres MCP d'OpenWebUI :

```json
{
  "mcpServers": {
    "csv-analyzer": {
      "command": "/opt/csv-analyzer-mcp/venv/bin/python",
      "args": ["/opt/csv-analyzer-mcp/mcp_server.py"]
    }
  }
}
```

## Gestion du Service

```bash
# Voir le statut
sudo systemctl status csv-analyzer-mcp

# Redémarrer
sudo systemctl restart csv-analyzer-mcp

# Voir les logs
sudo journalctl -u csv-analyzer-mcp -f

# Arrêter
sudo systemctl stop csv-analyzer-mcp
```

## Test du Serveur MCP

```bash
# Test basique (doit répondre aux requêtes JSON-RPC)
echo '{"jsonrpc": "2.0", "method": "initialize", "params": {}, "id": 1}' | \
/opt/csv-analyzer-mcp/venv/bin/python /opt/csv-analyzer-mcp/mcp_server.py
```

## Fichiers Importants

- `mcp_server.py` : Serveur MCP principal
- `deploy-mcp-server.sh` : Script de déploiement automatique
- `csv-analyzer-mcp.service` : Service systemd
- `requirements.txt` : Dépendances Python (FastMCP)
- `Dockerfile` : Image Docker pour le serveur MCP

## Sécurité

- Utilisateur système dédié (`mcp`)
- Sandbox E2B pour exécution isolée
- Pas d'exposition de ports réseau
- Communication via stdio uniquement

## Dépannage

### Service ne démarre pas
```bash
sudo journalctl -u csv-analyzer-mcp --no-pager -l
```

### Erreur de permissions
```bash
sudo chown -R mcp:mcp /opt/csv-analyzer-mcp
```

### MCP non détecté par OpenWebUI
Vérifier que le chemin dans la configuration MCP est correct et que le service est actif.