#!/usr/bin/env python3
"""
MCP Server pour CSV Analyzer avec E2B
Serveur MCP natif pour exposition via MCPO
"""

import asyncio
import tempfile
import os
import pandas as pd
import requests
import json
from typing import Any, Dict, List
from dotenv import load_dotenv
from e2b_code_interpreter import Sandbox
from mcp.server.fastmcp import FastMCP
from mcp.types import TextContent, Tool

# Charger les variables d'environnement
load_dotenv()

# Créer le serveur MCP
mcp = FastMCP("CSV Analyzer avec E2B")

def generate_crewai_agent_system_code(csv_structure, analysis_request):
    """Génère un système CrewAI d'agents intelligents collaboratifs"""
    
    columns = csv_structure.get('columns', [])
    dtypes = csv_structure.get('dtypes', {})
    
    # Analyser la demande utilisateur pour configurer les agents
    request_lower = analysis_request.lower()
    focus_temporal = any(word in request_lower for word in ['temps', 'temporal', 'évolution', 'tendance', 'time', 'chronolog'])
    focus_region = any(word in request_lower for word in ['région', 'region', 'géograph', 'zone', 'territorial'])
    focus_profit = any(word in request_lower for word in ['profit', 'rentabilité', 'marge', 'bénéfice', 'financier'])
    focus_satisfaction = any(word in request_lower for word in ['satisfaction', 'qualité', 'service', 'client'])
    focus_prediction = any(word in request_lower for word in ['prédic', 'forecast', 'futur', 'tendance', 'prévision'])
    focus_clustering = any(word in request_lower for word in ['segment', 'cluster', 'group', 'catégor', 'profil'])
    focus_research = any(word in request_lower for word in ['recherche', 'benchmark', 'comparaison', 'industrie', 'marché'])
    
    # Détecter les colonnes numériques et catégorielles
    numeric_cols = [col for col, dtype in dtypes.items() if 'int' in str(dtype) or 'float' in str(dtype)]
    categorical_cols = [col for col, dtype in dtypes.items() if 'object' in str(dtype)]
    
    # Système CrewAI d'agents intelligents collaboratifs
    code_template = f'''
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import warnings
import requests
from crewai import Agent, Task, Crew, Process
from crewai_tools import SerperDevTool, ScrapeWebsiteTool
warnings.filterwarnings('ignore')

# ==================== SYSTÈME CREWAI MULTI-AGENTS ====================
print("🚀 DÉMARRAGE DU SYSTÈME CREWAI MULTI-AGENTS D'ANALYSE")
print("=" * 70)

# Charger les données
df = pd.read_csv('dataset.csv')
print(f"📊 Dataset chargé: {{df.shape[0]}} lignes, {{df.shape[1]}} colonnes")

# Configuration des agents selon la demande utilisateur
agent_config = {{
    'temporal_focus': {focus_temporal},
    'regional_focus': {focus_region}, 
    'profit_focus': {focus_profit},
    'satisfaction_focus': {focus_satisfaction},
    'prediction_focus': {focus_prediction},
    'clustering_focus': {focus_clustering},
    'research_focus': {focus_research},
    'numeric_cols': {numeric_cols},
    'categorical_cols': {categorical_cols}
}}

print(f"🎯 Agents activés: {{[k.replace('_focus', '') for k, v in agent_config.items() if v == True and k.endswith('_focus')][:4]}}")
print()

# ==================== DÉFINITION DES AGENTS CREWAI ====================

# 🔍 AGENT DATA EXPLORER
data_explorer = Agent(
    role="Data Explorer Specialist",
    goal="Explore and understand data structure, quality, and patterns to provide foundation for analysis",
    backstory="""You are a meticulous data scientist with expertise in data quality assessment, 
    outlier detection, and statistical analysis. You always start with understanding the data 
    before diving into complex analysis.""",
    verbose=True,
    allow_delegation=False
)

# 🎨 AGENT VISUALIZATION MASTER
visualization_master = Agent(
    role="Data Visualization Expert", 
    goal="Create intelligent, adaptive visualizations that best represent the data insights",
    backstory="""You are a visualization expert who knows how to choose the perfect chart type 
    for each analysis. You create beautiful, informative graphics that tell the data story clearly.""",
    verbose=True,
    allow_delegation=False
)

# 🧠 AGENT ML INSIGHTS
ml_insights_agent = Agent(
    role="Machine Learning Analyst",
    goal="Apply advanced ML techniques for clustering, prediction and anomaly detection",
    backstory="""You are an expert in machine learning with deep knowledge of clustering algorithms, 
    predictive modeling, and statistical analysis. You find hidden patterns in data.""",
    verbose=True,
    allow_delegation=False
)

# 💼 AGENT BUSINESS INTELLIGENCE
business_intelligence = Agent(
    role="Business Intelligence Strategist",
    goal="Generate actionable business insights and strategic recommendations",
    backstory="""You are a senior business analyst with years of experience in translating 
    data insights into business value. You understand KPIs, market dynamics, and strategic planning.""",
    verbose=True,
    allow_delegation=False
)

# 🌐 AGENT INTERNET RESEARCH (NOUVEAU!)
internet_researcher = Agent(
    role="External Research Specialist",
    goal="Gather external market data, benchmarks, and industry insights to enrich analysis",
    backstory="""You are a skilled researcher who can find relevant external data sources, 
    industry benchmarks, and market insights to provide context to internal data analysis.""",
    verbose=True,
    allow_delegation=False,
    tools=[SerperDevTool(), ScrapeWebsiteTool()] if {focus_research} else []
)

# ==================== DÉFINITION DES TÂCHES CREWAI ====================

# 📊 TÂCHE EXPLORATION DES DONNÉES
data_exploration_task = Task(
    description=f"""Explore the CSV dataset thoroughly:
    1. Analyze data quality (missing values, outliers, data types)
    2. Generate descriptive statistics for all columns
    3. Identify key patterns and distributions
    4. Assess data completeness and reliability
    
    Dataset info: {{df.shape[0]}} rows, {{df.shape[1]}} columns
    Columns: {columns}
    Focus areas: {{[k.replace('_focus', '') for k, v in agent_config.items() if v == True and k.endswith('_focus')]}}
    """,
    expected_output="Comprehensive data quality report with statistics and patterns identified",
    agent=data_explorer
)

# 🎨 TÂCHE VISUALISATION
visualization_task = Task(
    description=f"""Create intelligent visualizations based on the data exploration results:
    1. Choose optimal chart types for the data
    2. Create temporal analysis if date columns exist
    3. Generate regional/categorical comparisons if applicable  
    4. Build correlation heatmaps for numeric data
    5. Design profit/margin analysis charts if financial data present
    
    Prioritize visualizations based on: {{'temporal' if focus_temporal else 'regional' if focus_region else 'profit' if focus_profit else 'general'}} analysis
    """,
    expected_output="Set of well-designed visualizations with insights annotations",
    agent=visualization_master,
    context=[data_exploration_task]
)

# 🧠 TÂCHE MACHINE LEARNING
ml_analysis_task = Task(
    description=f"""Apply advanced ML techniques:
    1. Perform clustering analysis if requested for customer segmentation
    2. Build predictive models if prediction focus is needed
    3. Detect statistical anomalies in the data
    4. Calculate feature importance and correlations
    5. Generate ML-driven insights
    
    ML focus areas: {{'clustering' if focus_clustering else 'prediction' if focus_prediction else 'general pattern detection'}}
    """,
    expected_output="ML analysis results with model performance metrics and insights",
    agent=ml_insights_agent,
    context=[data_exploration_task]
)

# 💼 TÂCHE BUSINESS INTELLIGENCE
business_insights_task = Task(
    description=f"""Generate actionable business insights:
    1. Calculate key business KPIs from the data
    2. Identify performance trends and opportunities
    3. Generate strategic recommendations
    4. Benchmark against expected business metrics
    5. Propose action items based on findings
    
    Business focus: {{'profitability' if focus_profit else 'customer satisfaction' if focus_satisfaction else 'operational efficiency'}}
    """,
    expected_output="Executive summary with KPIs, trends, and strategic recommendations",
    agent=business_intelligence,
    context=[data_exploration_task, ml_analysis_task]
)

# 🌐 TÂCHE RECHERCHE EXTERNE (Conditionnelle)
external_research_task = None
if {focus_research}:
    external_research_task = Task(
        description=f"""Research external context and benchmarks:
        1. Find industry benchmarks for key metrics
        2. Research market trends relevant to the data
        3. Gather competitive intelligence if applicable
        4. Identify external factors affecting performance
        5. Provide market context for internal data analysis
        """,
        expected_output="External research report with industry benchmarks and market context",
        agent=internet_researcher
    )

# ==================== ORCHESTRATION CREWAI ====================

# Définir les agents et tâches pour la crew
active_agents = [data_explorer, visualization_master, ml_insights_agent, business_intelligence]
active_tasks = [data_exploration_task, visualization_task, ml_analysis_task, business_insights_task]

if external_research_task:
    active_agents.append(internet_researcher)
    active_tasks.append(external_research_task)
    business_insights_task.context.append(external_research_task)

print(f"🎭 CREW ASSEMBLÉE: {{len(active_agents)}} agents, {{len(active_tasks)}} tâches")

# Créer la Crew CrewAI
analysis_crew = Crew(
    agents=active_agents,
    tasks=active_tasks,
    process=Process.sequential,
    verbose=True,
    memory=True
)

print("\\n🚀 LANCEMENT DE L'ANALYSE COLLABORATIVE...")
print("=" * 70)

# Exécuter l'analyse collaborative
try:
    result = analysis_crew.kickoff()
    
    print("\\n📋 RÉSULTATS DE L'ANALYSE COLLABORATIVE")
    print("=" * 70)
    print(result)
    
    print("\\n🏆 MISSION ACCOMPLIE - Analyse CrewAI Terminée")
    print("=" * 70)
    
except Exception as e:
    print(f"⚠️ Erreur dans l'exécution CrewAI: {{str(e)}}")
    print("Passage en mode analyse classique...")
    
    # Fallback: analyse classique si CrewAI échoue
    # ==================== ANALYSE CLASSIQUE FALLBACK ====================
class DataExplorerAgent:
    def __init__(self, data):
        self.data = data
        self.insights = []
    
    def explore(self):
        print("🔍 AGENT DATA EXPLORER - Exploration intelligente des données")
        print("-" * 50)
        
        # Analyse de qualité
        missing_pct = (self.data.isnull().sum() / len(self.data) * 100).round(2)
        self.insights.append(f"Qualité données: {{len(missing_pct[missing_pct > 0])}} colonnes avec valeurs manquantes")
        
        # Détection d'outliers intelligente
        for col in {numeric_cols}:
            if col in self.data.columns:
                Q1 = self.data[col].quantile(0.25)
                Q3 = self.data[col].quantile(0.75)
                IQR = Q3 - Q1
                outliers = ((self.data[col] < (Q1 - 1.5 * IQR)) | (self.data[col] > (Q3 + 1.5 * IQR))).sum()
                if outliers > 0:
                    self.insights.append(f"{{col}}: {{outliers}} outliers détectés ({{outliers/len(self.data)*100:.1f}}%)")
        
        # Patterns automatiques
        if 'revenue' in self.data.columns and 'cost' in self.data.columns:
            self.data['profit_margin'] = (self.data['revenue'] - self.data['cost']) / self.data['revenue'] * 100
            avg_margin = self.data['profit_margin'].mean()
            self.insights.append(f"Marge bénéficiaire moyenne calculée: {{avg_margin:.1f}}%")
        
        print("\\n".join([f"• {{insight}}" for insight in self.insights]))
        return self.insights

# ==================== AGENT 2: VISUALIZATION MAESTRO 🎨 ====================  
class VisualizationAgent:
    def __init__(self, data, config):
        self.data = data
        self.config = config
        self.viz_count = 0
    
    def create_intelligent_visualizations(self):
        print("\\n🎨 AGENT VISUALIZATION - Création de visualisations optimales")
        print("-" * 50)
        
        # Viz adaptatives selon la demande
        if self.config['temporal_focus'] and 'date' in self.data.columns:
            self._create_temporal_analysis()
        
        if self.config['regional_focus'] and 'region' in self.data.columns:
            self._create_regional_analysis()
            
        if len(self.config['numeric_cols']) >= 2:
            self._create_correlation_heatmap()
            
        if self.config['profit_focus'] and 'revenue' in self.data.columns:
            self._create_profit_analysis()
            
        print(f"✅ {{self.viz_count}} visualisations intelligentes générées")
    
    def _create_temporal_analysis(self):
        try:
            self.data['date'] = pd.to_datetime(self.data['date'], errors='coerce')
            plt.figure(figsize=(14, 8))
            
            # Multi-subplot temporel intelligent
            if 'revenue' in self.data.columns:
                plt.subplot(2, 2, 1)
                temporal_revenue = self.data.groupby(self.data['date'].dt.to_period('M'))['revenue'].sum()
                temporal_revenue.plot(kind='line', marker='o', color='steelblue', linewidth=2)
                plt.title('📈 Évolution du Revenue (Temporel)', fontweight='bold')
                plt.xticks(rotation=45)
                
                # Trend analysis
                if len(temporal_revenue) > 2:
                    trend = "📈 Croissant" if temporal_revenue.iloc[-1] > temporal_revenue.iloc[0] else "📉 Décroissant"
                    plt.text(0.02, 0.98, trend, transform=plt.gca().transAxes, fontsize=10, 
                            verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
            
            if 'customer_satisfaction' in self.data.columns:
                plt.subplot(2, 2, 2)
                temporal_satisfaction = self.data.groupby(self.data['date'].dt.to_period('M'))['customer_satisfaction'].mean()
                temporal_satisfaction.plot(kind='line', marker='s', color='green', linewidth=2)
                plt.title('😊 Évolution Satisfaction Client', fontweight='bold')
                plt.xticks(rotation=45)
            
            plt.tight_layout()
            plt.show()
            self.viz_count += 1
        except Exception as e:
            print(f"⚠️ Analyse temporelle échouée: {{str(e)[:50]}}")
    
    def _create_regional_analysis(self):
        try:
            plt.figure(figsize=(12, 6))
            if 'revenue' in self.data.columns:
                regional_data = self.data.groupby('region')['revenue'].agg(['sum', 'mean', 'count'])
                
                plt.subplot(1, 2, 1)
                regional_data['sum'].plot(kind='bar', color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4'], alpha=0.8)
                plt.title('💰 Revenue Total par Région', fontweight='bold')
                plt.xticks(rotation=45)
                
                plt.subplot(1, 2, 2)
                plt.pie(regional_data['sum'], labels=regional_data.index, autopct='%1.1f%%', 
                       colors=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4'])
                plt.title('🥧 Répartition Revenue par Région', fontweight='bold')
                
            plt.tight_layout()
            plt.show()
            self.viz_count += 1
        except Exception as e:
            print(f"⚠️ Analyse régionale échouée: {{str(e)[:50]}}")
    
    def _create_correlation_heatmap(self):
        try:
            numeric_data = self.data[self.config['numeric_cols']].corr()
            plt.figure(figsize=(10, 8))
            mask = np.triu(np.ones_like(numeric_data, dtype=bool))
            sns.heatmap(numeric_data, mask=mask, annot=True, cmap='RdYlBu_r', center=0,
                       square=True, linewidths=0.5, cbar_kws={{"shrink": 0.8}})
            plt.title('🌡️ Matrice de Corrélation Intelligente', fontweight='bold', pad=20)
            plt.tight_layout()
            plt.show()
            self.viz_count += 1
        except Exception as e:
            print(f"⚠️ Heatmap corrélation échouée: {{str(e)[:50]}}")
    
    def _create_profit_analysis(self):
        try:
            if 'cost' in self.data.columns:
                self.data['profit'] = self.data['revenue'] - self.data['cost']
                self.data['margin_pct'] = (self.data['profit'] / self.data['revenue']) * 100
                
                plt.figure(figsize=(12, 8))
                
                plt.subplot(2, 2, 1)
                plt.scatter(self.data['revenue'], self.data['profit'], alpha=0.6, color='darkgreen')
                plt.xlabel('Revenue')
                plt.ylabel('Profit')
                plt.title('💎 Revenue vs Profit', fontweight='bold')
                
                plt.subplot(2, 2, 2)
                self.data['margin_pct'].hist(bins=15, alpha=0.7, color='gold', edgecolor='black')
                plt.xlabel('Marge (%)')
                plt.ylabel('Fréquence')
                plt.title('📊 Distribution des Marges', fontweight='bold')
                
                if 'region' in self.data.columns:
                    plt.subplot(2, 2, 3)
                    margin_by_region = self.data.groupby('region')['margin_pct'].mean()
                    margin_by_region.plot(kind='bar', color='orange', alpha=0.8)
                    plt.title('🏆 Marge Moyenne par Région', fontweight='bold')
                    plt.xticks(rotation=45)
                
                plt.tight_layout()
                plt.show()
                self.viz_count += 1
        except Exception as e:
            print(f"⚠️ Analyse profit échouée: {{str(e)[:50]}}")

# ==================== AGENT 3: ML INSIGHTS GENIUS 🧠 ====================
class MLInsightsAgent:
    def __init__(self, data, config):
        self.data = data
        self.config = config
        self.predictions = []
        self.clusters = []
    
    def generate_ai_insights(self):
        print("\\n🧠 AGENT ML INSIGHTS - Intelligence artificielle avancée")
        print("-" * 50)
        
        if self.config['clustering_focus'] and len(self.config['numeric_cols']) >= 2:
            self._perform_smart_clustering()
        
        if self.config['prediction_focus'] and 'revenue' in self.data.columns:
            self._create_prediction_model()
        
        self._detect_anomalies()
        return self.predictions + self.clusters
    
    def _perform_smart_clustering(self):
        try:
            # Préparation intelligente des données pour clustering
            features_for_clustering = self.data[self.config['numeric_cols']].fillna(self.data[self.config['numeric_cols']].mean())
            scaler = StandardScaler()
            scaled_features = scaler.fit_transform(features_for_clustering)
            
            # Clustering optimal (3-5 clusters selon la taille des données)
            optimal_k = min(4, max(2, len(self.data) // 10))
            kmeans = KMeans(n_clusters=optimal_k, random_state=42, n_init=10)
            clusters = kmeans.fit_predict(scaled_features)
            
            self.data['cluster'] = clusters
            
            # Analyse des clusters
            print(f"🎯 {{optimal_k}} segments clients identifiés par IA:")
            for i in range(optimal_k):
                cluster_data = self.data[self.data['cluster'] == i]
                cluster_size = len(cluster_data)
                if 'revenue' in cluster_data.columns:
                    avg_revenue = cluster_data['revenue'].mean()
                    print(f"  • Segment {{i+1}}: {{cluster_size}} clients (Revenue moy: {{avg_revenue:.0f}})")
                else:
                    print(f"  • Segment {{i+1}}: {{cluster_size}} éléments")
            
            # Visualisation des clusters
            if len(self.config['numeric_cols']) >= 2:
                plt.figure(figsize=(10, 6))
                scatter = plt.scatter(features_for_clustering.iloc[:, 0], features_for_clustering.iloc[:, 1], 
                                    c=clusters, cmap='viridis', alpha=0.6)
                plt.xlabel(self.config['numeric_cols'][0])
                plt.ylabel(self.config['numeric_cols'][1])
                plt.title('🎨 Segmentation Client par IA', fontweight='bold')
                plt.colorbar(scatter)
                plt.show()
                
            self.clusters.append(f"{{optimal_k}} segments identifiés avec clustering intelligent")
            
        except Exception as e:
            print(f"⚠️ Clustering échoué: {{str(e)[:50]}}")
    
    def _create_prediction_model(self):
        try:
            if len(self.config['numeric_cols']) >= 2 and 'revenue' in self.data.columns:
                # Préparation des features pour prédiction
                feature_cols = [col for col in self.config['numeric_cols'] if col != 'revenue']
                if len(feature_cols) >= 1:
                    X = self.data[feature_cols].fillna(self.data[feature_cols].mean())
                    y = self.data['revenue'].fillna(self.data['revenue'].mean())
                    
                    # Train/test split
                    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
                    
                    # Random Forest pour prédiction
                    rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
                    rf_model.fit(X_train, y_train)
                    
                    # Prédictions et métriques
                    y_pred = rf_model.predict(X_test)
                    r2 = r2_score(y_test, y_pred)
                    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
                    
                    print(f"🔮 Modèle prédictif Revenue créé:")
                    print(f"  • Précision (R²): {{r2:.3f}}")
                    print(f"  • Erreur moyenne: {{rmse:.0f}}")
                    
                    # Feature importance
                    feature_importance = pd.DataFrame({{
                        'feature': feature_cols,
                        'importance': rf_model.feature_importances_
                    }}).sort_values('importance', ascending=False)
                    
                    print(f"  • Variable la plus prédictive: {{feature_importance.iloc[0]['feature']}}")
                    
                    self.predictions.append(f"Modèle prédictif avec {{r2:.1%}} de précision")
                    
        except Exception as e:
            print(f"⚠️ Prédiction échouée: {{str(e)[:50]}}")
    
    def _detect_anomalies(self):
        try:
            anomalies_found = 0
            for col in self.config['numeric_cols']:
                if col in self.data.columns:
                    z_scores = np.abs((self.data[col] - self.data[col].mean()) / self.data[col].std())
                    anomalies = (z_scores > 3).sum()
                    anomalies_found += anomalies
            
            if anomalies_found > 0:
                print(f"⚡ {{anomalies_found}} anomalies détectées par IA")
                self.predictions.append(f"{{anomalies_found}} anomalies statistiques identifiées")
                
        except Exception as e:
            print(f"⚠️ Détection anomalies échouée: {{str(e)[:50]}}")

# ==================== AGENT 4: BUSINESS INTELLIGENCE STRATEGIST 💼 ====================
class BusinessIntelligenceAgent:
    def __init__(self, data, config):
        self.data = data
        self.config = config
        self.recommendations = []
    
    def generate_strategic_insights(self):
        print("\\n💼 AGENT BUSINESS INTELLIGENCE - Insights stratégiques")
        print("-" * 50)
        
        self._calculate_kpis()
        self._generate_recommendations()
        return self.recommendations
    
    def _calculate_kpis(self):
        kpis = {{}}
        
        if 'revenue' in self.data.columns:
            kpis['total_revenue'] = self.data['revenue'].sum()
            kpis['avg_revenue'] = self.data['revenue'].mean()
            
        if 'customer_satisfaction' in self.data.columns:
            kpis['avg_satisfaction'] = self.data['customer_satisfaction'].mean()
            kpis['satisfaction_above_4'] = (self.data['customer_satisfaction'] >= 4.0).sum()
            
        if 'revenue' in self.data.columns and 'cost' in self.data.columns:
            total_profit = (self.data['revenue'] - self.data['cost']).sum()
            kpis['total_profit'] = total_profit
            kpis['profit_margin'] = (total_profit / self.data['revenue'].sum()) * 100
        
        print("📊 KPIs Business calculés:")
        for kpi, value in kpis.items():
            if isinstance(value, float):
                print(f"  • {{kpi.replace('_', ' ').title()}}: {{value:.2f}}")
            else:
                print(f"  • {{kpi.replace('_', ' ').title()}}: {{value}}")
    
    def _generate_recommendations(self):
        print("\\n🎯 Recommandations stratégiques IA:")
        
        # Recommandations basées sur les données
        if 'region' in self.data.columns and 'revenue' in self.data.columns:
            region_performance = self.data.groupby('region')['revenue'].sum().sort_values(ascending=False)
            best_region = region_performance.index[0]
            worst_region = region_performance.index[-1]
            
            print(f"  • 🏆 Focus sur {{best_region}} (meilleure région)")
            print(f"  • 🔄 Améliorer stratégie en {{worst_region}}")
            self.recommendations.extend([f"Optimiser {{best_region}}", f"Restructurer {{worst_region}}"])
        
        if 'customer_satisfaction' in self.data.columns:
            avg_satisfaction = self.data['customer_satisfaction'].mean()
            if avg_satisfaction < 3.5:
                print(f"  • ⚠️ Satisfaction critique ({{avg_satisfaction:.1f}}/5) - Action urgente requise")
                self.recommendations.append("Plan d'amélioration satisfaction urgent")
            elif avg_satisfaction >= 4.0:
                print(f"  • ✅ Excellente satisfaction ({{avg_satisfaction:.1f}}/5) - Maintenir qualité")
                self.recommendations.append("Capitaliser sur satisfaction élevée")
        
        if 'revenue' in self.data.columns and 'cost' in self.data.columns:
            margins = (self.data['revenue'] - self.data['cost']) / self.data['revenue'] * 100
            avg_margin = margins.mean()
            if avg_margin < 20:
                print(f"  • 💰 Marge faible ({{avg_margin:.1f}}%) - Optimiser coûts")
                self.recommendations.append("Stratégie réduction coûts")
            else:
                print(f"  • 💎 Marge saine ({{avg_margin:.1f}}%) - Continuer expansion")
                self.recommendations.append("Stratégie croissance")

# ==================== ORCHESTRATEUR PRINCIPAL 🎭 ====================
print("\\n🎭 ORCHESTRATEUR - Coordination des agents intelligents")
print("=" * 70)

# Initialisation des agents
explorer = DataExplorerAgent(df)
visualizer = VisualizationAgent(df, agent_config)
ml_agent = MLInsightsAgent(df, agent_config)
business_agent = BusinessIntelligenceAgent(df, agent_config)

# Exécution coordonnée
explorer_insights = explorer.explore()
visualizer.create_intelligent_visualizations()
ml_insights = ml_agent.generate_ai_insights()
business_insights = business_agent.generate_strategic_insights()

# ==================== RAPPORT FINAL SYNTHÉTIQUE 📋 ====================
print("\\n📋 RAPPORT FINAL - Synthèse Intelligence Collective")
print("=" * 70)
print(f"🔍 Insights Exploration: {{len(explorer_insights)}} découvertes")
print(f"🎨 Visualisations: {{visualizer.viz_count}} graphiques intelligents")
print(f"🧠 ML Insights: {{len(ml_insights)}} analyses prédictives")
print(f"💼 Recommandations: {{len(business_insights)}} actions stratégiques")

print("\\n🏆 MISSION ACCOMPLIE - Analyse Multi-Agents Terminée")
print("=" * 70)
'''

    # Ajout d'analyses spécifiques selon la demande utilisateur et les données
    if ('revenue' in numeric_cols and 'date' in categorical_cols) or focus_temporal:
        code_template += '''
# Analyse temporelle du revenue
print("\\n=== ANALYSE TEMPORELLE REVENUE ===")
if 'date' in df.columns:
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df_temporal = df.groupby(df['date'].dt.to_period('M'))['revenue'].agg(['sum', 'mean', 'count'])
    print(df_temporal.tail())
    
    # Graphique temporel
    plt.figure(figsize=(12, 6))
    df.groupby(df['date'].dt.to_period('M'))['revenue'].sum().plot(kind='line', marker='o')
    plt.title('Évolution du chiffre d\\'affaires dans le temps')
    plt.xlabel('Période')
    plt.ylabel('Revenue total')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()
'''

    if ('region' in categorical_cols and len(numeric_cols) > 0) or focus_region:
        code_template += f'''
# Analyse par région
print("\\n=== ANALYSE PAR RÉGION ===")
if 'region' in df.columns:
    region_analysis = df.groupby('region')[{numeric_cols}].agg(['mean', 'sum', 'count'])
    print(region_analysis)
    
    # Graphique comparatif par région
    plt.figure(figsize=(10, 6))
    df.groupby('region')['revenue'].sum().plot(kind='bar', color=['skyblue', 'lightgreen', 'salmon'])
    plt.title('Revenue total par région')
    plt.xlabel('Région')
    plt.ylabel('Revenue total')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()
'''

    if len(numeric_cols) >= 2:
        code_template += f'''
# Analyse de corrélation
print("\\n=== CORRÉLATIONS ===")
correlation_matrix = df[{numeric_cols}].corr()
print(correlation_matrix)

# Heatmap des corrélations
plt.figure(figsize=(8, 6))
sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', center=0)
plt.title('Matrice de corrélation')
plt.tight_layout()
plt.show()
'''

    # Insights business adaptatifs
    code_template += '''
# Insights business
print("\\n=== INSIGHTS BUSINESS ===")
'''
    
    if 'customer_satisfaction' in numeric_cols or focus_satisfaction:
        code_template += '''
print(f"Satisfaction client moyenne: {df['customer_satisfaction'].mean():.2f}/5")
high_satisfaction = df[df['customer_satisfaction'] >= 4.0]
print(f"Pourcentage clients satisfaits (≥4.0): {len(high_satisfaction)/len(df)*100:.1f}%")
'''

    if ('revenue' in numeric_cols and 'cost' in numeric_cols) or focus_profit:
        code_template += '''
df['profit'] = df['revenue'] - df['cost']
df['margin'] = (df['profit'] / df['revenue']) * 100
print(f"Marge bénéficiaire moyenne: {df['margin'].mean():.1f}%")
print(f"Profit total: {df['profit'].sum():.0f}")
'''

    code_template += '''
print("\\n=== ANALYSE TERMINÉE ===")
'''

    return code_template

def generate_analysis_code(csv_path, analysis_request, csv_structure):
    """Wrapper pour le nouveau système CrewAI multi-agents"""
    return generate_crewai_agent_system_code(csv_structure, analysis_request)

def analyze_csv_with_guaranteed_results(csv_path_in_sandbox, analysis_request):
    """Analyse garantie avec génération automatique de code"""
    
    # 1. Analyser la structure du CSV
    df = pd.read_csv(csv_path_in_sandbox)
    csv_structure = {
        "columns": list(df.columns),
        "shape": list(df.shape),
        "dtypes": {k: str(v) for k, v in df.dtypes.to_dict().items()},
        "sample": df.head(3).astype(str).to_dict()
    }
    
    # 2. Générer le code d'analyse approprié
    analysis_code = generate_analysis_code(csv_path_in_sandbox, analysis_request, csv_structure)
    
    # 3. Exécuter dans E2B
    sbx = Sandbox.create()
    
    try:
        # Upload du CSV
        with open(csv_path_in_sandbox, "rb") as f:
            sbx.files.write("dataset.csv", f)
        
        # Exécution du code d'analyse
        execution = sbx.run_code(analysis_code)
        
        results = []
        
        if execution.error:
            results.append({
                "type": "error",
                "error": {
                    "name": execution.error.name,
                    "value": execution.error.value,
                    "traceback": execution.error.traceback
                }
            })
        else:
            # Traiter tous les résultats - Prioriser les charts interactifs
            for result in execution.results:
                if result.chart:
                    # Chart interactif E2B (prioritaire pour OpenWebUI)
                    chart_data = {
                        "type": "interactive_chart",
                        "chart_type": str(getattr(result.chart, 'type', 'BAR')),
                        "title": getattr(result.chart, 'title', 'Analyse des données'),
                        "x_label": getattr(result.chart, 'x_label', 'Variables'),
                        "y_label": getattr(result.chart, 'y_label', 'Valeurs'),
                        "x_unit": getattr(result.chart, 'x_unit', None),
                        "y_unit": getattr(result.chart, 'y_unit', None),
                        "elements": []
                    }
                    
                    if hasattr(result.chart, 'elements'):
                        for element in result.chart.elements:
                            chart_data["elements"].append({
                                "label": getattr(element, 'label', ''),
                                "value": float(getattr(element, 'value', 0)),
                                "group": getattr(element, 'group', '')
                            })
                    
                    results.append(chart_data)
                    
                    # Ajouter description textuelle du graphique
                    chart_description = f"""
📊 **{chart_data['title']}**
- Type: {chart_data['chart_type']}
- Axe X: {chart_data['x_label']}
- Axe Y: {chart_data['y_label']}
- Données: {len(chart_data['elements'])} éléments
"""
                    if chart_data['elements']:
                        chart_description += "\n**Valeurs:**\n"
                        for elem in chart_data['elements'][:5]:  # Limiter à 5 pour lisibilité
                            chart_description += f"- {elem['label']}: {elem['value']}\n"
                    
                    results.append({
                        "type": "chart_summary",
                        "content": chart_description
                    })
                
                elif result.png:
                    # PNG disponible mais problème d'affichage OpenWebUI
                    results.append({
                        "type": "chart_note",
                        "content": "📊 Graphique PNG généré (non affiché dans OpenWebUI due à limitation technique)"
                    })
                
                elif result.text:
                    # Sortie texte
                    results.append({
                        "type": "text",
                        "content": result.text
                    })
        
        # 4. Ajouter résumé de la structure des données
        results.insert(0, {
            "type": "dataset_info",
            "structure": csv_structure,
            "analysis_type": "comprehensive_automated"
        })
        
        return results
        
    finally:
        sbx.kill()

# Outil MCP 1: Analyse CSV depuis URL
@mcp.tool()
def analyze_csv_from_url(csv_url: str, analysis_request: str = "Analyze this dataset comprehensively") -> Dict[str, Any]:
    """
    Télécharge et analyse un fichier CSV depuis une URL publique.
    
    Args:
        csv_url: URL publique du fichier CSV à analyser
        analysis_request: Description de l'analyse souhaitée
    
    Returns:
        Résultats d'analyse avec graphiques et insights
    """
    try:
        # Télécharger le fichier CSV
        response = requests.get(csv_url, timeout=30)
        response.raise_for_status()
        
        # Sauvegarder temporairement
        with tempfile.NamedTemporaryFile(delete=False, suffix='.csv', mode='wb') as temp_file:
            temp_file.write(response.content)
            temp_csv_path = temp_file.name
        
        try:
            # Analyse garantie
            results = analyze_csv_with_guaranteed_results(temp_csv_path, analysis_request)
            
            return {
                "success": True,
                "results": results,
                "analysis_guaranteed": True,
                "method": "URL_DOWNLOAD",
                "source_url": csv_url
            }
        
        finally:
            if temp_csv_path and os.path.exists(temp_csv_path):
                os.unlink(temp_csv_path)
                
    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "error": f"Failed to download CSV from URL: {str(e)}",
            "help": "Make sure the CSV URL is publicly accessible"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Analysis failed: {str(e)}"
        }

# Outil MCP 2: Analyse CSV depuis contenu texte
@mcp.tool()
def analyze_csv_from_content(csv_content: str, analysis_request: str = "Analyze this dataset comprehensively") -> Dict[str, Any]:
    """
    Analyse un fichier CSV depuis son contenu texte.
    
    Args:
        csv_content: Contenu du fichier CSV en texte brut
        analysis_request: Description de l'analyse souhaitée
    
    Returns:
        Résultats d'analyse avec graphiques et insights
    """
    try:
        if not csv_content or csv_content.strip() == "":
            return {
                "success": False,
                "error": "csv_content cannot be empty"
            }
        
        # Créer un fichier temporaire avec le contenu CSV
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv', encoding='utf-8') as temp_file:
            temp_file.write(csv_content)
            temp_csv_path = temp_file.name
        
        try:
            # Vérifier que le CSV est valide
            df_test = pd.read_csv(temp_csv_path)
            if df_test.empty:
                return {
                    "success": False,
                    "error": "CSV content is empty or invalid format"
                }
            
            # Analyse garantie
            results = analyze_csv_with_guaranteed_results(temp_csv_path, analysis_request)
            
            return {
                "success": True,
                "results": results,
                "analysis_guaranteed": True,
                "method": "TEXT_CONTENT",
                "dataset_shape": list(df_test.shape),
                "columns": list(df_test.columns)
            }
        
        finally:
            if temp_csv_path and os.path.exists(temp_csv_path):
                os.unlink(temp_csv_path)
                
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to analyze CSV content: {str(e)}",
            "help": "Make sure the csv_content is valid CSV format"
        }

# Ressource MCP: Informations sur le service
@mcp.resource("service://info")
def get_service_info() -> str:
    """Informations sur le service CSV Analyzer"""
    return '''{{
        "service": "CrewAI Multi-Agent CSV Analyzer with E2B",
        "version": "4.0.0-CREWAI-COLLABORATIVE",
        "description": "Serveur MCP révolutionnaire utilisant CrewAI pour orchestrer des agents IA spécialisés qui collaborent dans l'analyse de données CSV",
        "capabilities": [
            "🤖 Système CrewAI de 5 agents IA spécialisés collaboratifs",
            "🔍 Data Explorer Specialist - Exploration intelligente des données",
            "🎨 Data Visualization Expert - Graphiques adaptatifs contextuels",
            "🧠 Machine Learning Analyst - IA prédictive et clustering avancé",
            "💼 Business Intelligence Strategist - Insights et recommandations",
            "🌐 External Research Specialist - Recherche web et benchmarks",
            "🎭 Orchestration séquentielle avec mémoire partagée",
            "🔒 Exécution sécurisée dans sandbox E2B",
            "📱 Compatible OpenWebUI via MCPO"
        ],
        "crewai_features": [
            "Collaboration intelligente entre agents",
            "Mémoire partagée et contexte persistant",
            "Délégation automatique de tâches",
            "Workflow séquentiel optimisé",
            "Outils web intégrés (SerperDev, WebScraper)"
        ],
        "agents": [
            "Data Explorer Specialist",
            "Data Visualization Expert", 
            "Machine Learning Analyst",
            "Business Intelligence Strategist",
            "External Research Specialist"
        ],
        "tools": [
            "analyze_csv_from_url",
            "analyze_csv_from_content"
        ],
        "powered_by": ["CrewAI Framework", "E2B Code Interpreter", "Multi-Agent Collaboration", "MCP", "MCPO", "Python"]
    }}'''

# Prompt MCP: Template d'analyse
@mcp.prompt()
def csv_analysis_prompt(dataset_description: str = "dataset", focus: str = "comprehensive analysis") -> str:
    """
    Template de prompt pour l'analyse CSV
    
    Args:
        dataset_description: Description du dataset
        focus: Type d'analyse à privilégier
    """
    return f"""Effectue une analyse {focus} approfondie de ce {dataset_description}.

L'analyse doit inclure :
- Statistiques descriptives détaillées
- Visualisations pertinentes (graphiques temporels, comparaisons, corrélations)
- Identification des tendances et patterns
- Insights business et recommandations
- Détection d'anomalies ou points d'intérêt

Utilise les outils d'analyse CSV disponibles pour obtenir des résultats complets avec graphiques interactifs."""

if __name__ == "__main__":
    # Démarrer le serveur MCP
    mcp.run()