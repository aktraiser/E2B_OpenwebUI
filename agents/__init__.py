"""
Agents CrewAI pour l'analyse de données
"""

from .data_explorer import DataExplorerAgent
from .visualizer import VisualizationAgent
from .ml_analyst import MLAnalystAgent
from .business_intel import BusinessIntelligenceAgent
from .researcher import ResearchAgent

__all__ = [
    'DataExplorerAgent',
    'VisualizationAgent', 
    'MLAnalystAgent',
    'BusinessIntelligenceAgent',
    'ResearchAgent'
]