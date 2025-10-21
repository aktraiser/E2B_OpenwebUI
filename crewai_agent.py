"""
CrewAI Agent with E2B Code Interpreter
This runs INSIDE the main E2B MCP sandbox
"""
from crewai.tools import tool
from crewai import Agent, Task, Crew, LLM
from e2b_code_interpreter import Sandbox
import os


@tool("Python Interpreter")
def execute_python(code: str) -> str:
    """
    Execute Python code and return the results.
    Uses E2B Code Interpreter in a nested sandbox.

    Args:
        code: Python code to execute

    Returns:
        Execution results as text
    """
    try:
        with Sandbox.create(timeout=300) as sandbox:  # 5 minutes max
            execution = sandbox.run_code(code)

            # Handle different result types
            if execution.error:
                return f"Error: {execution.error}"

            # Combine text output and results
            output = []
            if execution.text:
                output.append(execution.text)

            if execution.results:
                for result in execution.results:
                    if hasattr(result, 'text'):
                        output.append(result.text)
                    elif hasattr(result, 'data'):
                        output.append(str(result.data))

            return "\n".join(output) if output else "Code executed successfully (no output)"

    except Exception as e:
        return f"Execution error: {str(e)}"


@tool("Search Web")
def search_web(query: str) -> str:
    """
    Search the web using MCP tools available in the sandbox.
    This calls the MCP Gateway running in the same sandbox.

    Args:
        query: Search query

    Returns:
        Search results
    """
    import requests

    try:
        # MCP Gateway runs on localhost:8080 in the same sandbox
        response = requests.post(
            "http://localhost:8080/tools/call",
            json={
                "name": "browserbase_search",  # or whatever MCP tool name
                "arguments": {"query": query}
            },
            timeout=30
        )
        response.raise_for_status()
        result = response.json()

        # Extract content from MCP response
        content = result.get("content", [])
        if content and len(content) > 0:
            return content[0].get("text", "No results")
        return "No results found"

    except Exception as e:
        return f"Search error: {str(e)}"


def create_crew(task_description: str = None):
    """
    Create a CrewAI crew with E2B tools

    Args:
        task_description: The task to execute

    Returns:
        Configured Crew instance
    """
    # Define the agent
    python_executor = Agent(
        role='Research Developer',
        goal='Execute code and research tasks using available tools',
        backstory="""You are an expert developer and researcher with access to:
        - Python code execution via E2B sandbox
        - Web search capabilities via MCP

        You ALWAYS use tools when needed to accomplish tasks.
        For code-related tasks, use the execute_python tool.
        For research tasks, use the search_web tool.""",
        tools=[execute_python, search_web],
        llm=LLM(
            model="gpt-4o",
            api_key=os.getenv("OPENAI_API_KEY")
        ),
        verbose=True
    )

    # Define the task
    if not task_description:
        task_description = "Calculate how many r's are in the word 'strawberry'"

    execute_task = Task(
        description=task_description,
        agent=python_executor,
        expected_output="Complete solution with code execution or research results"
    )

    # Create the crew
    crew = Crew(
        agents=[python_executor],
        tasks=[execute_task],
        verbose=True
    )

    return crew


if __name__ == "__main__":
    # Example usage
    crew = create_crew("Calculate how many r's are in the word 'strawberry'")
    result = crew.kickoff()
    print("\n" + "="*50)
    print("RESULT:")
    print("="*50)
    print(result)
