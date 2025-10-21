# 📋 Deployment Checklist

Utilisez cette checklist avant de déployer sur votre VPS.

## ✅ Pré-déploiement

### 1. Configuration
- [ ] Copier `.env.example` vers `.env`
- [ ] Ajouter votre `OPENAI_API_KEY` dans `.env`
- [ ] Ajouter votre `E2B_API_KEY` dans `.env`
- [ ] Ajuster `MAX_CONCURRENT_SANDBOXES` selon votre budget
- [ ] Ajuster `MAX_SANDBOXES_PER_HOUR` selon votre budget
- [ ] Vérifier les timeouts sont appropriés

### 2. VPS Prérequis
- [ ] VPS avec minimum 2GB RAM
- [ ] VPS avec minimum 2 CPU cores
- [ ] Docker installé (`docker --version`)
- [ ] Docker Compose installé (`docker-compose --version`)
- [ ] Port 8000 disponible
- [ ] Accès SSH configuré

### 3. Validation Locale
- [ ] Tester localement: `python main.py`
- [ ] Vérifier pas d'erreurs de configuration
- [ ] Confirmer les clés API fonctionnent

## 🚀 Déploiement

### 1. Upload sur VPS
```bash
# Exemple avec scp
scp -r E2B/ user@your-vps-ip:/opt/crewai/

# Ou avec rsync
rsync -avz E2B/ user@your-vps-ip:/opt/crewai/
```

### 2. Connexion VPS
```bash
ssh user@your-vps-ip
cd /opt/crewai
```

### 3. Déploiement
```bash
# Rendre le script exécutable
chmod +x deploy.sh

# Déployer
./deploy.sh
```

### 4. Vérification
- [ ] Health check: `curl http://localhost:8000/health`
- [ ] Metrics: `curl http://localhost:8000/metrics`
- [ ] Logs: `docker-compose logs -f crewai`
- [ ] Pas d'erreurs dans les logs

## 📊 Post-déploiement

### 1. Monitoring Initial (Première Heure)
- [ ] Vérifier création sandbox fonctionne
- [ ] Vérifier exécution code fonctionne
- [ ] Vérifier métriques se mettent à jour
- [ ] Vérifier logs sont écrits correctement
- [ ] Tester endpoint health toutes les 10 min

### 2. Monitoring Continue (Premier Jour)
- [ ] Vérifier pas de dépassement hourly limit
- [ ] Vérifier pas de crash/restart
- [ ] Surveiller usage CPU/RAM VPS
- [ ] Vérifier rotation des logs
- [ ] Noter le coût E2B après 24h

### 3. Configuration Firewall (si nécessaire)
```bash
# Si vous voulez exposer le health check
sudo ufw allow 8000/tcp

# Pour accès externe
# Configurer reverse proxy (nginx/caddy)
```

## 💰 Budget Tracking

### Métriques à Surveiller
1. **Coût quotidien E2B**
   - Vérifier dashboard E2B
   - Comparer avec métriques `/metrics`

2. **Usage VPS**
   ```bash
   # CPU/RAM
   htop
   
   # Disk
   df -h
   
   # Docker stats
   docker stats crewai-e2b
   ```

### Alertes Recommandées
- [ ] Alert si `hourly_count` > 18 (90% de la limite)
- [ ] Alert si `failure_rate` > 10%
- [ ] Alert si coût E2B > budget quotidien
- [ ] Alert si VPS RAM > 80%

## 🔧 Maintenance

### Quotidienne
- [ ] Vérifier health endpoint
- [ ] Consulter métriques
- [ ] Vérifier coûts E2B

### Hebdomadaire
- [ ] Analyser logs pour patterns
- [ ] Ajuster limites si nécessaire
- [ ] Nettoyer vieux logs
- [ ] Update dependencies si nécessaire

### Mensuelle
- [ ] Review coût total E2B
- [ ] Optimiser configuration
- [ ] Update Docker images
- [ ] Backup configuration

## 🆘 Troubleshooting

### Service ne démarre pas
```bash
docker-compose logs crewai
docker-compose down
docker-compose build --no-cache
docker-compose up
```

### Coûts trop élevés
1. Vérifier `/metrics` pour usage anormal
2. Réduire `MAX_SANDBOXES_PER_HOUR`
3. Réduire `MAX_CONCURRENT_SANDBOXES`
4. Redémarrer: `docker-compose restart`

### Health check fail
```bash
# Vérifier logs
docker-compose logs --tail=100 crewai

# Vérifier .env
cat .env | grep API_KEY

# Tester manuellement
docker-compose exec crewai python -c "from config import VPSConfig; print(VPSConfig.validate())"
```

## 📞 Support

Si problème persiste:
1. Sauvegarder les logs: `docker-compose logs > debug.log`
2. Sauvegarder les métriques: `curl http://localhost:8000/metrics > metrics.json`
3. Vérifier configuration: `cat .env` (masquer les clés)
4. Vérifier structure: `ls -la`

---

**Date de déploiement**: _________________

**Déployé par**: _________________

**Budget E2B mensuel**: _________________

**Notes**:
