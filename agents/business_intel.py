"""
Agent Business Intelligence - Stratège Business
"""

from crewai import Agent
from crewai.tools import tool

@tool("KPI Calculator")
def calculate_kpis(data_summary: str) -> str:
    """
    Calcule les KPIs business critiques
    """
    return f"KPIs calculated from {data_summary}"

@tool("Business Recommender")
def generate_recommendations(analysis_results: str) -> str:
    """
    Génère des recommandations business basées sur l'analyse
    """
    return f"Generated strategic recommendations based on {analysis_results}"

@tool("ROI Analyzer")
def analyze_roi(investment_data: str) -> str:
    """
    Analyse le retour sur investissement
    """
    return f"ROI analysis completed for {investment_data}"

def create_business_intelligence_agent():
    """
    Crée l'agent Business Intelligence avec ses outils
    """
    return Agent(
        role='Business Intelligence Strategist',
        goal='Transform data insights into actionable business strategies',
        backstory="""You are a business strategist with expertise in:
        - KPI development and tracking
        - Strategic planning
        - ROI analysis
        - Market trend analysis
        - Competitive intelligence
        You translate complex data into clear business recommendations.""",
        tools=[calculate_kpis, generate_recommendations, analyze_roi],
        verbose=True,
        allow_delegation=False
    )

# Alias pour compatibilité
BusinessIntelligenceAgent = create_business_intelligence_agent