#!/bin/bash

# Script de mise à jour MCPO CSV Analyzer
# Usage: ./update-mcpo.sh

set -e

echo "🔄 Mise à jour du serveur MCPO CSV Analyzer"

# Variables
SERVICE_NAME="csv-analyzer-mcpo"
APP_DIR="/opt/csv-analyzer-mcpo"

# 1. Arrêter le service
echo "⏹️  Arrêt du service..."
sudo systemctl stop $SERVICE_NAME

# 2. Mettre à jour les fichiers
echo "📋 Mise à jour des fichiers..."
sudo cp mcp_server.py $APP_DIR/
sudo cp csv-analyzer-mcpo.service /etc/systemd/system/$SERVICE_NAME.service

# 3. Recharger et redémarrer
echo "🔄 Rechargement du service..."
sudo systemctl daemon-reload
sudo systemctl start $SERVICE_NAME

# 4. Vérifier le statut
echo "📊 Vérification du statut..."
sleep 5
if sudo systemctl is-active --quiet $SERVICE_NAME; then
    echo "✅ Service $SERVICE_NAME mis à jour avec succès"
    sudo systemctl status $SERVICE_NAME --no-pager -l
    echo ""
    echo "🧪 Test de l'API:"
    curl -I http://147.93.94.85:8091/docs || echo "⚠️  API pas encore disponible (normal pendant le démarrage)"
else
    echo "❌ Erreur lors du redémarrage du service"
    sudo systemctl status $SERVICE_NAME --no-pager -l
    echo "📋 Logs du service:"
    sudo journalctl -u $SERVICE_NAME --no-pager -l -n 20
    exit 1
fi

echo ""
echo "🎉 Mise à jour terminée !"
echo "📍 API disponible sur: http://147.93.94.85:8091"
echo "📖 Documentation: http://147.93.94.85:8091/docs"