#!/usr/bin/env python3
"""
Serveur MCP pour l'analyse CSV avec CrewAI et E2B
Version modulaire et simplifiée
"""

import os
import tempfile
from typing import Dict, Any
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from mcp.types import TextContent
from sandbox import execute_crew_in_sandbox
import pandas as pd
import requests

# Charger les variables d'environnement
load_dotenv()

# Initialiser le serveur MCP
mcp = FastMCP("CSV Analyzer CrewAI")

@mcp.tool()
def analyze_csv_from_content(csv_content: str, analysis_request: str) -> Dict[str, Any]:
    """
    Analyse un fichier CSV avec le système CrewAI multi-agents
    
    Args:
        csv_content: Contenu du fichier CSV en texte brut
        analysis_request: Description de l'analyse souhaitée
    
    Returns:
        Résultats d'analyse avec graphiques et insights
    """
    try:
        # Créer un fichier temporaire pour le CSV
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
            f.write(csv_content)
            temp_csv_path = f.name
        
        # Analyser la structure du CSV
        df = pd.read_csv(temp_csv_path)
        
        print(f"📊 Analyse de {df.shape[0]} lignes et {df.shape[1]} colonnes")
        print(f"🎯 Demande: {analysis_request}")
        
        # Exécuter l'analyse CrewAI dans le sandbox E2B
        results = execute_crew_in_sandbox(temp_csv_path, analysis_request)
        
        # Nettoyer
        os.unlink(temp_csv_path)
        
        # Ajouter des métadonnées
        results['metadata'] = {
            'rows': df.shape[0],
            'columns': df.shape[1],
            'column_names': df.columns.tolist(),
            'analysis_type': 'CrewAI Multi-Agent Analysis'
        }
        
        return results
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'message': 'Erreur lors de l\'analyse CrewAI'
        }

@mcp.tool()
def analyze_csv_from_url(csv_url: str, analysis_request: str) -> Dict[str, Any]:
    """
    Télécharge et analyse un fichier CSV depuis une URL publique
    
    Args:
        csv_url: URL publique du fichier CSV à analyser
        analysis_request: Description de l'analyse souhaitée
    
    Returns:
        Résultats d'analyse avec graphiques et insights
    """
    try:
        # Télécharger le CSV
        print(f"📥 Téléchargement depuis {csv_url}")
        response = requests.get(csv_url)
        response.raise_for_status()
        
        # Analyser avec le contenu téléchargé
        return analyze_csv_from_content(response.text, analysis_request)
        
    except requests.RequestException as e:
        return {
            'success': False,
            'error': f'Erreur de téléchargement: {str(e)}',
            'message': 'Impossible de télécharger le fichier CSV'
        }

@mcp.tool()
def get_analysis_capabilities() -> Dict[str, Any]:
    """
    Retourne les capacités d'analyse disponibles
    
    Returns:
        Liste des agents et outils disponibles
    """
    return {
        'agents': [
            {
                'name': 'Data Explorer',
                'role': 'Exploration et qualité des données',
                'capabilities': ['Statistiques descriptives', 'Détection d\'outliers', 'Analyse de qualité']
            },
            {
                'name': 'Visualization Expert',
                'role': 'Création de visualisations',
                'capabilities': ['Graphiques adaptatifs', 'Tableaux de bord', 'Heatmaps']
            },
            {
                'name': 'ML Analyst',
                'role': 'Machine Learning',
                'capabilities': ['Clustering', 'Prédictions', 'Détection d\'anomalies']
            },
            {
                'name': 'Business Intelligence',
                'role': 'Insights business',
                'capabilities': ['KPIs', 'Recommandations stratégiques', 'ROI']
            },
            {
                'name': 'Research Specialist',
                'role': 'Recherche externe',
                'capabilities': ['Benchmarks industrie', 'Tendances marché', 'Meilleures pratiques']
            }
        ],
        'features': [
            'Analyse multi-agents collaborative',
            'Exécution sécurisée dans sandbox E2B',
            'Graphiques interactifs',
            'Insights basés sur l\'IA',
            'Recherche externe automatique'
        ],
        'supported_formats': ['CSV'],
        'max_file_size': '100MB'
    }

if __name__ == "__main__":
    print("🚀 Serveur MCP CrewAI démarré")
    print("📊 Système multi-agents prêt pour l'analyse")
    print("🤖 Agents disponibles: Data Explorer, Visualizer, ML Analyst, Business Intel, Researcher")
    mcp.run()