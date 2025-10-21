"""
CrewAI agents and crew definition for VPS deployment.
Optimized for E2B sandbox usage with cost awareness.
"""
from crewai import Agent, Task, Crew, Process, LLM
from crewai.project import CrewBase, agent, crew, task
from tools import execute_python
from config import VPSConfig
import logging

logger = logging.getLogger(__name__)


@CrewBase
class CodeExecutionCrewVPS:
    """
    Production-ready CrewAI crew for Python code execution on VPS.
    """

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
            llm=LLM(model="gpt-4o", temperature=0.1),
            verbose=True,
            allow_delegation=False,
            max_iter=VPSConfig.MAX_ITERATIONS,
            max_rpm=VPSConfig.MAX_RPM
        )

    @task
    def execute_task(self) -> Task:
        """Main execution task."""
        return Task(
            description="""Calculate how many times the letter 'r' appears in the word 'strawberry'.

IMPORTANT:
- Think analytically first
- Consider if you can solve without running code
- If code is needed, write optimal code that runs once
- Each execution costs money

Choose the most efficient approach.""",
            agent=self.python_executor(),
            expected_output="""Clear answer with:
1. The exact count of 'r' in 'strawberry'
2. Your reasoning
3. Code used (if any)
4. Verification"""
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
