# 🔧 Quick Fix - Rebuild Docker

Le problème était que `mcpo` utilise un environnement isolé et ne peut pas accéder aux dépendances.

## Solution

Créé un serveur FastAPI direct (`api_server.py`) au lieu d'utiliser `mcpo`.

## Rebuild sur le VPS

```bash
ssh root@147.93.94.85

cd /root/E2B_OpenwebUI  # ou votre dossier

# Pull les derniers changements
git pull

# Rebuild le container
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# Vérifier les logs
docker-compose logs -f
```

## Test

Une fois que les logs montrent:
```
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

Tester l'API:

```bash
curl http://147.93.94.85:8000/docs
```

Devrait afficher la page Swagger UI!

## Configuration OpenWebUI

Maintenant dans OpenWebUI:

1. **Settings** → **Functions** → **+ Add Function**
2. **OpenAPI Function**
3. **URL**: `http://147.93.94.85:8000/openapi.json`
4. **Activer**

Prêt! 🚀
