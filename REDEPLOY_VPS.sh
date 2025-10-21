#!/bin/bash
# Script pour redéployer le fix sur VPS

echo "🔧 Redéploiement du fix Agent Not Executing"
echo "==========================================="
echo ""

# Vérifier que crew.py existe
if [ ! -f "crew.py" ]; then
    echo "❌ Erreur: crew.py non trouvé"
    echo "Lancez ce script depuis le dossier E2B/"
    exit 1
fi

echo "📋 Étapes:"
echo "1. Copier crew.py vers VPS"
echo "2. Redémarrer le container"
echo "3. Tester l'exécution"
echo ""

# Demander l'IP du VPS
read -p "IP du VPS (ex: srv1070106 ou 123.45.67.89): " VPS_IP
read -p "Utilisateur SSH (ex: root): " VPS_USER
read -p "Chemin du projet sur VPS (ex: ~/E2B_OpenwebUI): " VPS_PATH

echo ""
echo "📤 Copie de crew.py vers VPS..."
scp crew.py ${VPS_USER}@${VPS_IP}:${VPS_PATH}/crew.py

if [ $? -ne 0 ]; then
    echo "❌ Erreur lors de la copie"
    exit 1
fi

echo "✅ Fichier copié"
echo ""

echo "🔄 Redémarrage du container sur VPS..."
ssh ${VPS_USER}@${VPS_IP} "cd ${VPS_PATH} && docker-compose restart"

if [ $? -ne 0 ]; then
    echo "❌ Erreur lors du redémarrage"
    exit 1
fi

echo "✅ Container redémarré"
echo ""

echo "⏳ Attente 10 secondes pour le démarrage..."
sleep 10

echo "🧪 Test de l'exécution..."
ssh ${VPS_USER}@${VPS_IP} << 'SSHEOF'
cd ~/E2B_OpenwebUI
echo "Test API execute endpoint..."
curl -X POST http://localhost:8000/execute \
  -H "Content-Type: application/json" \
  -d '{"task": "Calculate 5 + 3 using Python"}'
echo ""
echo ""
echo "Vérification des métriques..."
curl http://localhost:8000/metrics | grep -E "total_executions|total_created"
SSHEOF

echo ""
echo "✅ Redéploiement terminé!"
echo ""
echo "📊 Prochaines étapes:"
echo "1. Vérifier les logs: ssh ${VPS_USER}@${VPS_IP} 'docker logs crewai-e2b --tail 50'"
echo "2. Tester avec votre tâche: curl -X POST http://${VPS_IP}:8000/execute -H 'Content-Type: application/json' -d '{\"task\":\"votre tâche\"}'"
echo "3. Monitorer métriques: curl http://${VPS_IP}:8000/metrics"
