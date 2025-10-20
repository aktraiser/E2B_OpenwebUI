# Structure du Projet CrewAI Multi-Agents

## 🏗️ Architecture Modulaire

Le projet est maintenant organisé de façon claire et modulaire :

```
E2B/
├── mcp_server_new.py       # 🚀 Serveur MCP principal (simple et court)
│
├── agents/                 # 🤖 Agents CrewAI spécialisés
│   ├── data_explorer.py    # Agent exploration de données
│   ├── visualizer.py       # Agent visualisation
│   ├── ml_analyst.py       # Agent Machine Learning
│   ├── business_intel.py   # Agent Business Intelligence
│   └── researcher.py       # Agent recherche externe
│
├── crews/                  # 🎭 Orchestration des agents
│   └── analysis_crew.py    # Crew principal d'analyse
│
├── tools/                  # 🔧 Outils CrewAI
│   ├── data_tools.py       # Outils d'analyse de données
│   └── viz_tools.py        # Outils de visualisation
│
└── sandbox/                # 📦 Exécution sécurisée
    └── executor.py         # Exécuteur E2B sandbox
```

## 🎯 Avantages de cette Structure

### 1. **Clarté** 
- Chaque agent a son propre fichier
- Responsabilités bien séparées
- Code facile à naviguer

### 2. **Maintenabilité**
- Modifications isolées par composant
- Pas d'impact sur les autres modules
- Debug plus facile

### 3. **Réutilisabilité**
- Import simple des agents
- Outils partagés entre agents
- Crews personnalisables

### 4. **Évolutivité**
- Ajout facile de nouveaux agents
- Nouvelles capacités sans refonte
- Tests unitaires par module

## 🔄 Flux d'Exécution

1. **OpenWebUI** → Envoie requête d'analyse
2. **mcp_server_new.py** → Reçoit et route la requête
3. **sandbox/executor.py** → Prépare l'environnement E2B
4. **crews/analysis_crew.py** → Orchestre les agents
5. **agents/*.py** → Chaque agent fait son travail
6. **tools/*.py** → Outils utilisés par les agents
7. **E2B Sandbox** → Exécution sécurisée du code
8. **Résultats** → Retour vers OpenWebUI

## 🚀 Utilisation

### Pour démarrer le serveur :
```bash
python mcp_server_new.py
```

### Pour tester localement :
```python
from sandbox import execute_crew_in_sandbox

results = execute_crew_in_sandbox(
    csv_data="date,revenue\n2024-01-01,1000\n2024-01-02,1500",
    analysis_request="Analyse complète avec prédictions"
)
```

## 📦 Installation

```bash
pip install crewai e2b-code-interpreter pandas matplotlib seaborn
```

## 🤖 Agents Disponibles

### Data Explorer 🔍
- Analyse qualité des données
- Statistiques descriptives
- Détection d'outliers

### Visualizer 🎨
- Graphiques intelligents
- Tableaux de bord
- Choix automatique du type de graphique

### ML Analyst 🧠
- Clustering
- Prédictions
- Détection d'anomalies

### Business Intelligence 💼
- KPIs
- Recommandations stratégiques
- Analyse ROI

### Researcher 🌐
- Benchmarks industrie
- Tendances marché
- Comparaisons externes

## 🔐 Sécurité

Tout le code s'exécute dans le sandbox E2B :
- Isolation complète
- Pas d'accès au système hôte
- Environnement contrôlé

## 📈 Prochaines Étapes

1. Ajouter plus d'outils spécialisés
2. Intégrer des LLMs locaux
3. Support de formats additionnels (Excel, JSON)
4. Interface web de configuration
5. Métriques et monitoring