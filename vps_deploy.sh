#!/bin/bash

# Script de déploiement pour VPS - SÉCURISÉ
# Les clés API doivent être configurées dans des variables d'environnement

echo "🚀 Déploiement sur VPS..."

# Variables de configuration
VPS_USER="${VPS_USER:-root}"
VPS_IP="${VPS_IP:-YOUR_VPS_IP}"
VPS_PATH="${VPS_PATH:-/root/E2B_OpenwebUI}"

# Vérifier que les clés sont définies dans l'environnement
if [ -z "$ANTHROPIC_API_KEY" ] || [ -z "$E2B_API_KEY" ]; then
    echo "❌ Erreur: Les clés API doivent être définies dans l'environnement"
    echo ""
    echo "Utilisation:"
    echo "  export ANTHROPIC_API_KEY='sk-ant-api03-...'"
    echo "  export E2B_API_KEY='e2b_...'"
    echo "  ./vps_deploy.sh"
    echo ""
    echo "OU sourcez votre fichier .env existant:"
    echo "  source .env && ./vps_deploy.sh"
    exit 1
fi

# Créer le fichier .env temporaire SANS les clés en dur
cat > /tmp/temp.env << EOF
# API Keys (depuis variables d'environnement)
ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
E2B_API_KEY=${E2B_API_KEY}

# Resource Limits
MAX_CONCURRENT_SANDBOXES=${MAX_CONCURRENT_SANDBOXES:-2}
MAX_SANDBOXES_PER_HOUR=${MAX_SANDBOXES_PER_HOUR:-20}
CODE_EXECUTION_TIMEOUT=${CODE_EXECUTION_TIMEOUT:-30.0}
LOG_LEVEL=${LOG_LEVEL:-INFO}
EOF

echo "📤 Transfert des fichiers vers ${VPS_USER}@${VPS_IP}:${VPS_PATH}..."

# Transférer tous les fichiers sauf .git, logs et .env
rsync -avz --exclude='.git' --exclude='logs/*' --exclude='.env' --exclude='.env.local' \
    ./ ${VPS_USER}@${VPS_IP}:${VPS_PATH}/

# Transférer le .env sécurisé
echo "🔐 Transfert sécurisé du fichier de configuration..."
scp /tmp/temp.env ${VPS_USER}@${VPS_IP}:${VPS_PATH}/.env

# Nettoyer le fichier temporaire
rm -f /tmp/temp.env

echo "🔧 Configuration sur le VPS..."

# Exécuter les commandes sur le VPS
ssh ${VPS_USER}@${VPS_IP} << ENDSSH
cd ${VPS_PATH}
mkdir -p logs
chmod +x deploy.sh
echo "📦 Construction et démarrage des conteneurs..."
./deploy.sh
ENDSSH

echo ""
echo "✅ Déploiement terminé!"
echo ""
echo "📊 Vérifier le statut:"
echo "   ssh ${VPS_USER}@${VPS_IP} 'curl http://localhost:8000/health'"
echo ""
echo "📋 Voir les logs:"
echo "   ssh ${VPS_USER}@${VPS_IP} 'cd ${VPS_PATH} && docker-compose logs -f'"
echo ""
echo "⚠️  N'oubliez pas de vérifier que vos clés API sont correctes!"