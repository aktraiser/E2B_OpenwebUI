"""
Crew d'analyse - Orchestration des agents CrewAI
"""

from crewai import Crew, Task, Process, LLM
from agents import (
    DataExplorerAgent,
    VisualizationAgent,
    MLAnalystAgent,
    BusinessIntelligenceAgent,
    ResearchAgent
)

class AnalysisCrew:
    """
    Orchestrateur principal pour l'analyse de données avec CrewAI
    """
    
    def __init__(self, csv_path: str, analysis_request: str):
        self.csv_path = csv_path
        self.analysis_request = analysis_request
        self.llm = LLM(model="gpt-4o")
        
    def setup_agents(self):
        """
        Configure tous les agents nécessaires
        """
        self.data_explorer = DataExplorerAgent()
        self.visualizer = VisualizationAgent()
        self.ml_analyst = MLAnalystAgent()
        self.business_analyst = BusinessIntelligenceAgent()
        self.researcher = ResearchAgent()
        
    def create_tasks(self):
        """
        Crée les tâches pour chaque agent
        """
        # Tâche 1: Explorer les données
        self.explore_task = Task(
            description=f"""
            Analyze the CSV file at {self.csv_path}:
            1. Check data quality and completeness
            2. Generate descriptive statistics
            3. Identify patterns and outliers
            4. Prepare data summary for other agents
            
            User request: {self.analysis_request}
            """,
            agent=self.data_explorer,
            expected_output="Comprehensive data quality report with statistics"
        )
        
        # Tâche 2: Créer des visualisations
        self.visualize_task = Task(
            description=f"""
            Create visualizations based on the data exploration:
            1. Choose appropriate chart types
            2. Generate key insights visualizations
            3. Create comparison charts if applicable
            4. Build a visual summary dashboard
            
            Focus on: {self.analysis_request}
            """,
            agent=self.visualizer,
            expected_output="Set of meaningful visualizations with insights",
            context=[self.explore_task]
        )
        
        # Tâche 3: Analyse ML
        self.ml_task = Task(
            description=f"""
            Apply machine learning techniques:
            1. Perform clustering if relevant
            2. Build predictive models if applicable
            3. Detect anomalies in the data
            4. Calculate feature importance
            
            Analysis focus: {self.analysis_request}
            """,
            agent=self.ml_analyst,
            expected_output="ML insights with model results and predictions",
            context=[self.explore_task]
        )
        
        # Tâche 4: Analyse Business
        self.business_task = Task(
            description=f"""
            Generate business insights:
            1. Calculate key business metrics
            2. Identify opportunities and risks
            3. Generate strategic recommendations
            4. Provide actionable next steps
            
            Business context: {self.analysis_request}
            """,
            agent=self.business_analyst,
            expected_output="Strategic business recommendations with KPIs",
            context=[self.explore_task, self.visualize_task, self.ml_task]
        )
        
        # Tâche 5: Recherche externe (optionnelle)
        if "benchmark" in self.analysis_request.lower() or "market" in self.analysis_request.lower():
            self.research_task = Task(
                description=f"""
                Research external information:
                1. Find industry benchmarks
                2. Gather market trends
                3. Compare with competitors
                4. Find best practices
                
                Research focus: {self.analysis_request}
                """,
                agent=self.researcher,
                expected_output="External research findings and benchmarks"
            )
            return [self.explore_task, self.visualize_task, self.ml_task, self.research_task, self.business_task]
        
        return [self.explore_task, self.visualize_task, self.ml_task, self.business_task]
    
    def run(self):
        """
        Exécute l'analyse complète avec tous les agents
        """
        # Configuration
        self.setup_agents()
        tasks = self.create_tasks()
        
        # Créer la crew
        crew = Crew(
            agents=[
                self.data_explorer,
                self.visualizer,
                self.ml_analyst,
                self.business_analyst,
                self.researcher if hasattr(self, 'research_task') else None
            ],
            tasks=tasks,
            process=Process.sequential,
            verbose=True,
            memory=True
        )
        
        # Filtrer les agents None
        crew.agents = [a for a in crew.agents if a is not None]
        
        # Exécuter l'analyse
        print("🚀 Lancement de l'analyse CrewAI multi-agents...")
        result = crew.kickoff()
        
        return result