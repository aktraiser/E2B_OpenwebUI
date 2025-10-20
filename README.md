# CSV Analyzer MCPO - OpenWebUI Integration

Service d'analyse de fichiers CSV avec E2B Code Interpreter utilisant MCPO (MCP-to-OpenAPI proxy) pour intégration OpenWebUI.

## 🚀 Architecture

- **Serveur MCP natif** avec FastMCP
- **MCPO Proxy** qui expose le MCP server via OpenAPI REST
- **E2B Code Interpreter** pour exécution sécurisée  
- **Déploiement VPS** sur port 8091
- **Intégration OpenWebUI** via External Tools

```
OpenWebUI → http://147.93.94.85:8091 → MCPO → MCP Server → E2B
```

## 📋 Prérequis

- Docker et Docker Compose
- Clé API E2B ([obtenir ici](https://e2b.dev))
- Clé API Anthropic ([obtenir ici](https://console.anthropic.com))

## 🛠️ Installation

1. **Cloner le projet**
```bash
git clone <your-repo>
cd E2B
```

2. **Configuration des variables d'environnement**
```bash
cp .env.example .env
```

Éditer `.env` avec vos clés API :
```env
E2B_API_KEY=your_e2b_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
PORT=8000
```

3. **Build et démarrage**
```bash
docker-compose up -d --build
```

## 🔧 Utilisation

### API Endpoints

#### Health Check
```bash
GET /health
```

#### Analyser un CSV
```bash
POST /analyze
Content-Type: multipart/form-data

csv_file: [fichier CSV]
analysis_request: "Analyse les tendances de vente par mois" (optionnel)
```

### Exemple d'usage

```bash
curl -X POST http://localhost:8091/analyze \
  -F "csv_file=@your_data.csv" \
  -F "analysis_request=Analyser les tendances temporelles et créer des graphiques"
```

### Réponse

```json
{
  "success": true,
  "results": [
    {
      "type": "interactive_chart",
      "chart_type": "line",
      "title": "Évolution des ventes",
      "x_label": "Mois",
      "y_label": "Revenus",
      "elements": [
        {
          "label": "Jan",
          "value": 1000,
          "group": "Ventes"
        }
      ]
    },
    {
      "type": "text",
      "content": "Les ventes montrent une tendance croissante..."
    }
  ]
}
```

## 🌐 Déploiement VPS

### Docker traditionnel
```bash
# Sur le VPS
git clone <your-repo>
cd E2B
cp .env.example .env
# Configurer les clés API dans .env
docker-compose up -d --build
```

### Avec Nginx (recommandé)
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:8091;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        client_max_body_size 50M;
    }
}
```

## 🔗 Intégration OpenWebUI

Dans OpenWebUI, vous pouvez créer une fonction personnalisée :

```python
import requests

def analyze_csv(csv_file_path, analysis_request="Analyze this dataset"):
    with open(csv_file_path, 'rb') as f:
        files = {'csv_file': f}
        data = {'analysis_request': analysis_request}
        
        response = requests.post(
            'http://your-vps:8091/analyze',
            files=files,
            data=data
        )
        
    return response.json()
```

## 📊 Types de Charts Supportés

- **Line charts** : Tendances temporelles
- **Bar charts** : Comparaisons catégorielles  
- **Scatter plots** : Corrélations
- **Pie charts** : Répartitions
- **Box plots** : Distributions statistiques

## 🛡️ Sécurité

- Utilisateur non-root dans le container
- Limite de taille de fichier (50MB)
- Nettoyage automatique des fichiers temporaires
- Health checks intégrés

## 🔧 Monitoring

```bash
# Logs en temps réel
docker-compose logs -f csv-analyzer

# Status des containers
docker-compose ps

# Redémarrer le service
docker-compose restart csv-analyzer
```

## 🚨 Dépannage

### Erreurs communes

1. **API Keys manquantes**
   - Vérifier `.env`
   - Redémarrer le container

2. **Limite de mémoire**
   - Ajuster les limites dans `docker-compose.yml`

3. **Timeout sur gros fichiers**
   - Augmenter le timeout gunicorn
   - Vérifier les ressources VPS

### Support

Pour des problèmes spécifiques, vérifier :
- [Documentation E2B](https://e2b.dev/docs)
- [Documentation Anthropic](https://docs.anthropic.com)
- Logs du container : `docker-compose logs csv-analyzer`