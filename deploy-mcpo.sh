#!/bin/bash

# Script de déploiement MCPO CSV Analyzer sur VPS
# Usage: ./deploy-mcpo.sh

set -e

echo "🚀 Déploiement du serveur MCPO CSV Analyzer"

# Variables
APP_DIR="/opt/csv-analyzer-mcpo"
SERVICE_NAME="csv-analyzer-mcpo"
USER_NAME="mcpo"
PORT=8091

# 1. Créer l'utilisateur système
echo "👤 Création de l'utilisateur système..."
if ! id "$USER_NAME" &>/dev/null; then
    sudo useradd --system --home-dir $APP_DIR --shell /bin/bash $USER_NAME
    echo "✅ Utilisateur $USER_NAME créé"
else
    echo "ℹ️  Utilisateur $USER_NAME existe déjà"
fi

# 2. Créer le répertoire d'application
echo "📁 Création du répertoire d'application..."
sudo mkdir -p $APP_DIR
sudo chown $USER_NAME:$USER_NAME $APP_DIR

# 3. Installer Python et dépendances
echo "🐍 Installation de Python et pip..."
sudo apt-get update
sudo apt-get install -y python3 python3-pip python3-venv gcc g++

# 4. Créer l'environnement virtuel
echo "🔧 Création de l'environnement virtuel..."
sudo -u $USER_NAME python3 -m venv $APP_DIR/venv

# 5. Copier les fichiers d'application
echo "📋 Copie des fichiers d'application..."
sudo cp mcp_server.py $APP_DIR/
sudo cp requirements.txt $APP_DIR/
sudo cp .env $APP_DIR/ 2>/dev/null || echo "⚠️  Fichier .env non trouvé, créez-le manuellement"

# 6. Installer les dépendances Python
echo "📦 Installation des dépendances Python..."
sudo -u $USER_NAME $APP_DIR/venv/bin/pip install --upgrade pip
sudo -u $USER_NAME $APP_DIR/venv/bin/pip install -r $APP_DIR/requirements.txt

# 7. Configurer les permissions
echo "🔐 Configuration des permissions..."
sudo chown -R $USER_NAME:$USER_NAME $APP_DIR

# 8. Installer le service systemd pour MCPO
echo "⚙️  Installation du service systemd MCPO..."
sudo cp csv-analyzer-mcpo.service /etc/systemd/system/$SERVICE_NAME.service

sudo systemctl daemon-reload
sudo systemctl enable $SERVICE_NAME

# 9. Configurer les variables d'environnement
echo "🔧 Configuration des variables d'environnement..."
if [ ! -f "$APP_DIR/.env" ]; then
    sudo -u $USER_NAME tee $APP_DIR/.env > /dev/null <<EOF
E2B_API_KEY=your_e2b_api_key_here
EOF
    echo "⚠️  Fichier .env créé. Modifiez $APP_DIR/.env avec vos vraies clés API"
fi

# 10. Démarrer le service
echo "🚀 Démarrage du service MCPO..."
sudo systemctl start $SERVICE_NAME

# 11. Vérifier le statut
echo "📊 Vérification du statut..."
sleep 10
if sudo systemctl is-active --quiet $SERVICE_NAME; then
    echo "✅ Service $SERVICE_NAME démarré avec succès"
    sudo systemctl status $SERVICE_NAME --no-pager -l
else
    echo "❌ Erreur lors du démarrage du service"
    sudo systemctl status $SERVICE_NAME --no-pager -l
    echo "📋 Logs du service:"
    sudo journalctl -u $SERVICE_NAME --no-pager -l
    exit 1
fi

echo ""
echo "🎉 Déploiement MCPO terminé !"
echo ""
echo "📍 Informations importantes:"
echo "  - API MCPO disponible sur: http://147.93.94.85:$PORT"
echo "  - Documentation OpenAPI: http://147.93.94.85:$PORT/docs"
echo "  - OpenAPI spec: http://147.93.94.85:$PORT/openapi.json"
echo "  - Service systemd: $SERVICE_NAME"
echo "  - Répertoire: $APP_DIR"
echo ""
echo "🔧 Configuration OpenWebUI:"
echo "  Settings → Admin → External Tools"
echo "  URL: http://147.93.94.85:$PORT"
echo ""
echo "📖 Outils disponibles:"
echo "  - analyze_csv_from_url"
echo "  - analyze_csv_from_content" 
echo ""
echo "⚠️  N'oubliez pas de:"
echo "  1. Modifier $APP_DIR/.env avec vos vraies clés API"
echo "  2. Redémarrer: sudo systemctl restart $SERVICE_NAME"
echo "  3. Tester l'API: curl http://147.93.94.85:$PORT/docs"