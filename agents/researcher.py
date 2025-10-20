"""
Agent Research - Chercheur externe et benchmarks
"""

from crewai import Agent
from crewai_tools import SerperDevTool, ScrapeWebsiteTool

def create_research_agent():
    """
    Crée l'agent Research avec outils de recherche web
    """
    # Outils de recherche externe
    search_tool = SerperDevTool()
    scrape_tool = ScrapeWebsiteTool()
    
    return Agent(
        role='External Research Specialist',
        goal='Find relevant industry benchmarks, trends, and external insights',
        backstory="""You are a research specialist who:
        - Searches for industry benchmarks and standards
        - Finds relevant market trends and comparisons
        - Gathers competitive intelligence
        - Identifies best practices in the industry
        - Provides context from external sources
        You enrich internal data analysis with external perspectives.""",
        tools=[search_tool, scrape_tool],
        verbose=True,
        allow_delegation=False
    )

# Alias pour compatibilité
ResearchAgent = create_research_agent