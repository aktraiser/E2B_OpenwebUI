"""
Agent Visualization - Expert en visualisation de données
"""

from crewai import Agent
from crewai.tools import tool

@tool("Chart Creator")
def create_chart(chart_type: str, x_col: str, y_col: str) -> str:
    """
    Crée un graphique et retourne sa description
    """
    return f"Created {chart_type} chart: {y_col} by {x_col}"

@tool("Dashboard Builder")
def build_dashboard(metrics: str) -> str:
    """
    Construit un tableau de bord avec les métriques clés
    """
    return f"Dashboard created with metrics: {metrics}"

def create_visualization_agent():
    """
    Crée l'agent Visualization avec ses outils
    """
    return Agent(
        role='Data Visualization Expert',
        goal='Create intelligent, adaptive visualizations that best represent data insights',
        backstory="""You are a visualization expert who:
        - Knows how to choose the perfect chart type for each analysis
        - Creates beautiful, informative graphics
        - Tells the data story clearly through visuals
        - Masters color theory and design principles""",
        tools=[create_chart, build_dashboard],
        verbose=True,
        allow_delegation=False
    )

# Alias pour compatibilité
VisualizationAgent = create_visualization_agent