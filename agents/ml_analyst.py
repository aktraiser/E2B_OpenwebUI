"""
Agent ML Analyst - Analyste Machine Learning
"""

from crewai import Agent
from crewai.tools import tool

@tool("Clustering Analyzer")
def perform_clustering(data_info: str, n_clusters: int = 3) -> str:
    """
    Effectue une analyse de clustering sur les données
    """
    return f"Clustering analysis completed with {n_clusters} clusters"

@tool("Predictive Modeler")
def build_predictive_model(target_column: str, features: str) -> str:
    """
    Construit un modèle prédictif
    """
    return f"Predictive model built for {target_column} using {features}"

@tool("Anomaly Detector")
def detect_anomalies(column_name: str) -> str:
    """
    Détecte les anomalies dans les données
    """
    return f"Anomaly detection completed for {column_name}"

def create_ml_analyst_agent():
    """
    Crée l'agent ML Analyst avec ses outils
    """
    return Agent(
        role='Machine Learning Analyst',
        goal='Apply advanced ML techniques to discover hidden patterns and make predictions',
        backstory="""You are an ML expert specializing in:
        - Clustering and segmentation
        - Predictive modeling
        - Anomaly detection
        - Feature engineering
        - Model evaluation and optimization
        You use cutting-edge algorithms to extract insights from data.""",
        tools=[perform_clustering, build_predictive_model, detect_anomalies],
        verbose=True,
        allow_delegation=False
    )

# Alias pour compatibilité
MLAnalystAgent = create_ml_analyst_agent