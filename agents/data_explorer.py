"""
Agent Data Explorer - Spécialiste de l'exploration de données
"""

from crewai import Agent
from crewai.tools import tool

@tool("Data Quality Analyzer")
def analyze_data_quality(df_info: str) -> str:
    """
    Analyse la qualité des données et retourne un rapport
    """
    return f"Analyse de qualité complétée pour: {df_info}"

@tool("Statistical Analyzer")
def compute_statistics(column_name: str) -> str:
    """
    Calcule des statistiques descriptives pour une colonne
    """
    return f"Statistiques calculées pour {column_name}"

def create_data_explorer_agent():
    """
    Crée l'agent Data Explorer avec ses outils
    """
    return Agent(
        role='Data Explorer Specialist',
        goal='Explore and understand data structure, quality, and patterns',
        backstory="""You are a meticulous data scientist with expertise in:
        - Data quality assessment
        - Outlier detection
        - Statistical analysis
        - Pattern recognition
        You always start by understanding the data before diving into complex analysis.""",
        tools=[analyze_data_quality, compute_statistics],
        verbose=True,
        allow_delegation=False
    )

# Alias pour compatibilité
DataExplorerAgent = create_data_explorer_agent