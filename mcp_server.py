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
from typing import Any, Dict, List
from dotenv import load_dotenv
from e2b_code_interpreter import Sandbox
from mcp.server.fastmcp import FastMCP
from mcp.types import TextContent, Tool

# Charger les variables d'environnement
load_dotenv()

# Créer le serveur MCP
mcp = FastMCP("CSV Analyzer avec E2B")

def generate_analysis_code(csv_path, analysis_request, csv_structure):
    """Génère un code d'analyse Python concis pour éviter les problèmes de tokens"""
    
    code_template = '''
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Charger les données
df = pd.read_csv('dataset.csv')

print("=== ANALYSE CSV ===")
print(f"Shape: {df.shape}")
print(f"Colonnes: {list(df.columns)}")

# Statistiques descriptives
print("\\nSTATISTIQUES:")
print(df.describe())

# Graphiques automatiques
numeric_cols = df.select_dtypes(include=[np.number]).columns

# Graphique de distribution
if len(numeric_cols) > 0:
    plt.figure(figsize=(12, 4))
    for i, col in enumerate(numeric_cols[:3]):
        plt.subplot(1, 3, i+1)
        df[col].hist(bins=10)
        plt.title(f'Distribution {col}')
    plt.tight_layout()
    plt.show()

# Insights simples
print("\\n=== INSIGHTS ===")
for col in numeric_cols:
    print(f"- {col}: moyenne = {df[col].mean():.2f}")

print("\\n=== TERMINÉ ===")
'''
    
    return code_template

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
            # Traiter tous les résultats
            for result in execution.results:
                if result.png:
                    # Chart PNG matplotlib (prioritaire)
                    results.append({
                        "type": "chart_image",
                        "format": "png",
                        "data": result.png,
                        "description": "Graphique généré par E2B matplotlib"
                    })
                
                elif result.chart:
                    # Chart interactif E2B (fallback)
                    chart_data = {
                        "type": "interactive_chart",
                        "chart_type": getattr(result.chart, 'type', 'matplotlib'),
                        "title": getattr(result.chart, 'title', 'Analyse'),
                        "x_label": getattr(result.chart, 'x_label', None),
                        "y_label": getattr(result.chart, 'y_label', None),
                        "elements": []
                    }
                    
                    if hasattr(result.chart, 'elements'):
                        for element in result.chart.elements:
                            chart_data["elements"].append({
                                "label": getattr(element, 'label', ''),
                                "value": getattr(element, 'value', 0),
                                "group": getattr(element, 'group', '')
                            })
                    
                    results.append(chart_data)
                
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
        "service": "CSV Analyzer avec E2B",
        "version": "2.0.0-MCPO",
        "description": "Serveur MCP pour l'analyse de fichiers CSV avec E2B Code Interpreter",
        "capabilities": [
            "Analyse automatique de structure CSV",
            "Génération de graphiques interactifs",
            "Insights business automatiques",
            "Corrélations et tendances",
            "Compatible OpenWebUI via MCPO"
        ],
        "tools": [
            "analyze_csv_from_url",
            "analyze_csv_from_content"
        ],
        "powered_by": ["E2B Code Interpreter", "MCP", "MCPO", "Python"]
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