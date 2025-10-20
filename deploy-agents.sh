#!/bin/bash

# Script de déploiement du système CrewAI multi-agents
echo "🚀 DÉPLOIEMENT DU SYSTÈME CREWAI MULTI-AGENTS"
echo "=" * 60

# Variables
VPS_IP="147.93.94.85"
VPS_USER="root"
APP_DIR="/opt/csv-analyzer-mcpo"
SERVICE_NAME="csv-analyzer-mcpo"

echo "📋 Copie des fichiers CrewAI..."
scp mcp_server.py ${VPS_USER}@${VPS_IP}:${APP_DIR}/
scp requirements.txt ${VPS_USER}@${VPS_IP}:${APP_DIR}/

echo "🔄 Mise à jour avec CrewAI sur VPS..."
ssh ${VPS_USER}@${VPS_IP} << EOF
    cd ${APP_DIR}
    
    # Installation des nouvelles dépendances CrewAI
    echo "📦 Installation CrewAI et outils..."
    ${APP_DIR}/venv/bin/pip install --upgrade crewai crewai-tools
    ${APP_DIR}/venv/bin/pip install --upgrade scikit-learn
    
    # Redémarrage du service CrewAI
    echo "🔄 Redémarrage du service CrewAI..."
    systemctl restart ${SERVICE_NAME}
    
    # Vérification
    sleep 15
    if systemctl is-active --quiet ${SERVICE_NAME}; then
        echo "✅ Système CrewAI déployé avec succès"
        systemctl status ${SERVICE_NAME} --no-pager -l
        
        echo ""
        echo "🧪 Test de l'API CrewAI:"
        curl -I http://147.93.94.85:8091/docs || echo "⚠️ API pas encore disponible (normal pendant le démarrage)"
    else
        echo "❌ Erreur lors du déploiement CrewAI"
        systemctl status ${SERVICE_NAME} --no-pager -l
        echo "📋 Logs du service:"
        journalctl -u ${SERVICE_NAME} --no-pager -l -n 30
        exit 1
    fi
EOF

echo ""
echo "🎉 DÉPLOIEMENT CREWAI TERMINÉ !"
echo "🚀 Le système CrewAI multi-agents est maintenant actif:"
echo "   📍 API: http://147.93.94.85:8091"
echo "   📖 Documentation: http://147.93.94.85:8091/docs"
echo ""
echo "🤖 AGENTS CREWAI DISPONIBLES:"
echo "   🔍 Data Explorer Specialist - Exploration intelligente des données"
echo "   🎨 Data Visualization Expert - Graphiques adaptatifs et contextuels"
echo "   🧠 Machine Learning Analyst - IA prédictive et clustering avancé"
echo "   💼 Business Intelligence Strategist - Insights et recommandations"
echo "   🌐 External Research Specialist - Recherche web et benchmarks"
echo ""
echo "🎭 ORCHESTRATION CREWAI:"
echo "   ✅ Collaboration séquentielle intelligente"
echo "   ✅ Mémoire partagée entre agents"
echo "   ✅ Délégation automatique de tâches"
echo "   ✅ Outils web intégrés (SerperDev, WebScraper)"