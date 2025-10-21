"""
CrewAI agents and crew definition for VPS deployment.
Optimized for E2B sandbox usage with cost awareness.
"""
from crewai import Agent, Task, Crew, Process, LLM
from crewai.project import CrewBase, agent, crew, task
from tools import execute_python
from config import VPSConfig
import logging
import os

logger = logging.getLogger(__name__)


@CrewBase
class CodeExecutionCrewVPS:
    """
    Production-ready CrewAI crew for Python code execution on VPS.
    """
    
    def __init__(self):
        self._custom_task = None
    
    def set_custom_task(self, task_description: str):
        """Set a custom task description"""
        self._custom_task = task_description

    @agent
    def python_executor(self) -> Agent:
        """Python code execution agent with cost awareness."""
        return Agent(
            role="Senior Python Code Executor",
            goal="Execute Python code efficiently with minimal resource usage",
            backstory="""You are an experienced Python developer working on a production VPS.
            Every code execution creates a cloud sandbox which costs money.

            Your approach:
            1. Think through problems logically first
            2. Validate code mentally before execution
            3. Write optimal, efficient code
            4. Only execute when absolutely necessary

            You excel at writing correct code on the first try, minimizing retries.""",
            tools=[execute_python],
            llm=LLM(
                model="gpt-4o-mini",  # ou "gpt-4o" pour le modèle complet
                api_key=os.getenv("OPENAI_API_KEY")
            ),
            verbose=True,
            allow_delegation=False,
            max_iter=VPSConfig.MAX_ITERATIONS,
            max_rpm=VPSConfig.MAX_RPM
        )

    @task
    def execute_task(self) -> Task:
        """Main execution task."""
        # Use custom task if provided, otherwise default task
        if self._custom_task:
            description = self._custom_task
            expected_output = """Clear answer with:
1. The exact result
2. Your reasoning
3. Code used (if any)
4. Verification"""
        else:
            description = """Calculate how many times the letter 'r' appears in the word 'strawberry'."""
            expected_output = """Clear answer with:
1. The exact count of 'r' in 'strawberry'
2. Your reasoning
3. Code used (if any)
4. Verification"""
        
        description += """

IMPORTANT:
- Think analytically first
- Consider if you can solve without running code
- If code is needed, write optimal code that runs once
- Each execution costs money

Choose the most efficient approach."""
        
        return Task(
            description=description,
            agent=self.python_executor(),
            expected_output=expected_output
        )

    @crew
    def crew(self) -> Crew:
        """Creates the code execution crew."""
        return Crew(
            agents=[self.python_executor()],
            tasks=[self.execute_task()],
            process=Process.sequential,
            verbose=True,
            max_rpm=VPSConfig.MAX_RPM
        )
