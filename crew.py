"""
CrewAI setup for E2B MCP integration
"""
from crewai import Agent, Task, Crew
from tools import execute_python, search_duckduckgo, search_arxiv, list_mcp_tools


def create_crew(task_description: str = None):
    """Create a crew with MCP tools"""
    
    # Research agent with MCP capabilities
    agent = Agent(
        role="Research Developer",
        goal="Execute code and research using MCP servers in E2B sandbox",
        backstory="""You are a researcher and developer with access to:
        - Python code execution in E2B sandbox
        - DuckDuckGo search via MCP
        - ArXiv paper search via MCP
        - Direct MCP tool access
        
        Use these tools to solve tasks comprehensively.""",
        tools=[execute_python, search_duckduckgo, search_arxiv, list_mcp_tools],
        verbose=True
    )
    
    # Task
    if not task_description:
        task_description = "Calculate how many times the letter 'r' appears in 'strawberry'"
    
    task = Task(
        description=f"""
        Task: {task_description}
        
        Steps:
        1. First list available MCP tools
        2. Use appropriate tools to solve the task
        3. If needed, execute Python code
        4. Provide comprehensive results
        """,
        agent=agent,
        expected_output="Complete solution with tool usage details"
    )
    
    return Crew(
        agents=[agent],
        tasks=[task],
        verbose=True
    )