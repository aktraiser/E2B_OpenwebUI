"""
MCP Server for VPS - Simple Version
Exposes E2B + CrewAI tools to OpenWebUI via MCP protocol

Simple approach using E2B Code Interpreter + CrewAI directly
"""
import asyncio
import json
import logging
from typing import Any
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
from e2b_code_interpreter import Sandbox
from crewai.tools import tool
from crewai import Agent, Task, Crew, LLM
import os
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("e2b-crewai-mcp")

@tool("Python Interpreter")
def execute_python(code: str) -> str:
    """
    Execute Python code and return the results.
    """
    try:
        with Sandbox.create() as sandbox:
            execution = sandbox.run_code(code)
            if execution.error:
                return f"Error: {execution.error}"
            return execution.text if execution.text else "Code executed successfully"
    except Exception as e:
        return f"Execution error: {str(e)}"


@tool("Web Crawler")
def crawl_website(url: str) -> str:
    """
    Advanced web crawler that extracts clean markdown content from websites.
    
    Args:
        url: The website URL to crawl
    
    Returns:
        Clean markdown content from the website
    """
    try:
        with Sandbox.create() as sandbox:
            crawl_code = f"""
import subprocess
import sys
import json

# Install and setup crawl4ai
try:
    from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
    print("✅ Crawl4AI already available")
except ImportError:
    print("📦 Installing Crawl4AI...")
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-U', 'crawl4ai'])
    print("🔧 Setting up Crawl4AI (this may take a few minutes)...")
    subprocess.check_call(['crawl4ai-setup'])
    print("🎭 Installing Playwright browsers...")
    subprocess.check_call(['playwright', 'install'])
    from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
    print("✅ Crawl4AI setup complete")

import asyncio

async def crawl_site():
    url = "{url}"
    
    print("=== CRAWL4AI DEBUG START ===")
    print(f"Target URL: {{url}}")
    
    # First: Test basic connectivity
    try:
        import requests
        response = requests.get(url, timeout=10)
        print(f"✅ Basic requests test: {{response.status_code}}")
        print(f"✅ Content length: {{len(response.text)}}")
        if len(response.text) > 0:
            print(f"✅ Content preview: {{response.text[:200]}}...")
    except Exception as e:
        print(f"❌ Basic requests failed: {{e}}")
    
    # Modern Crawl4AI configuration with proper browser and crawler configs
    try:
        from crawl4ai import BrowserConfig
        print("✅ BrowserConfig imported successfully")
    except Exception as e:
        print(f"❌ BrowserConfig import failed: {{e}}")
        from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
        browser_config = None
    else:
        browser_config = BrowserConfig(
            headless=True,
            user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
        )
        print(f"✅ BrowserConfig created: {{browser_config}}")
    
    crawler_config = CrawlerRunConfig(
        wait_until="domcontentloaded",
        page_timeout=60000,  # 60 seconds timeout
        wait_for="css:body",  # Proper CSS selector syntax
        word_count_threshold=5,
        exclude_external_links=True,
        exclude_social_media_links=True
    )
    print(f"✅ CrawlerRunConfig created: {{crawler_config}}")
    
    print("\\n=== STARTING CRAWL4AI ===")
    print(f"Browser config: {{browser_config is not None}}")
    print(f"Crawler config: {{crawler_config}}")
    
    try:
        if browser_config:
            async with AsyncWebCrawler(config=browser_config) as crawler:
                print("✅ AsyncWebCrawler created with BrowserConfig")
                result = await crawler.arun(url=url, config=crawler_config)
        else:
            async with AsyncWebCrawler() as crawler:
                print("✅ AsyncWebCrawler created without BrowserConfig")
                result = await crawler.arun(url=url, config=crawler_config)
        
        print(f"\\n=== CRAWL4AI RESULT DEBUG ===")
        print(f"Success: {{result.success}}")
        print(f"Status code: {{getattr(result, 'status_code', 'N/A')}}")
        print(f"Error message: {{getattr(result, 'error_message', 'N/A')}}")
        print(f"Markdown length: {{len(result.markdown) if result.markdown else 0}}")
        print(f"Cleaned HTML length: {{len(result.cleaned_html) if result.cleaned_html else 0}}")
        print(f"Raw HTML length: {{len(result.html) if result.html else 0}}")
        print(f"Metadata: {{result.metadata}}")
        
        if result.success:
            markdown = result.markdown or result.cleaned_html or result.html or "No content in any format"
            
            if markdown and len(markdown.strip()) > 0:
                # Smart content truncation
                if len(markdown) > 8000:
                    # Try to cut at a logical point (paragraph break)
                    truncate_at = markdown.find('\\n\\n', 7000)
                    if truncate_at > 0:
                        markdown = markdown[:truncate_at] + "\\n\\n[Content truncated at paragraph break...]"
                    else:
                        markdown = markdown[:8000] + "\\n\\n[Content truncated...]"
                
                print("\\n=== SUCCESSFUL CRAWL RESULTS ===")
                print(f"URL: {{url}}")
                print(f"Title: {{result.metadata.get('title', 'N/A')}}")
                print(f"Description: {{result.metadata.get('description', 'N/A')[:100]}}...")
                print(f"Word Count: {{len(markdown.split())}}")
                print("\\n=== CONTENT ===")
                print(markdown)
            else:
                print("❌ SUCCESS=True but no content found in markdown/cleaned_html/html")
                print(f"Available attributes: {{dir(result)}}")
                # Try to extract with basic selectors
                if result.html:
                    print("\\n=== TRYING BASIC HTML PARSING ===")
                    from bs4 import BeautifulSoup
                    soup = BeautifulSoup(result.html, 'html.parser')
                    titles = soup.select('.titleline > a')
                    print(f"Found {{len(titles)}} .titleline > a elements")
                    for i, title in enumerate(titles[:5]):
                        print(f"{{i+1}}. {{title.get_text()}} -> {{title.get('href', 'no href')}}")
        else:
            print(f"❌ CRAWL FAILED")
            print(f"Error: {{result.error_message}}")
            print(f"Status: {{getattr(result, 'status_code', 'N/A')}}")
            
            # Fallback with simpler config
            print("\\n=== FALLBACK TO SIMPLE CRAWL ===")
            simple_config = CrawlerRunConfig(
                wait_until="domcontentloaded",
                page_timeout=30000,
                word_count_threshold=1
            )
            if browser_config:
                async with AsyncWebCrawler(config=browser_config) as fallback_crawler:
                    basic_result = await fallback_crawler.arun(url=url, config=simple_config)
            else:
                async with AsyncWebCrawler() as fallback_crawler:
                    basic_result = await fallback_crawler.arun(url=url, config=simple_config)
            
            if basic_result.success:
                content = basic_result.markdown[:5000] if basic_result.markdown else "No content"
                print(f"Basic content extracted: {{len(content)}} characters")
                print(content)
            else:
                print(f"Both enhanced and basic crawling failed: {{basic_result.error_message}}")
                    
    except Exception as e:
        print(f"Crawling error: {{e}}")
        # Final fallback with minimal config
        try:
            minimal_browser = BrowserConfig(headless=True)
            minimal_config = CrawlerRunConfig(page_timeout=15000)
            async with AsyncWebCrawler(config=minimal_browser) as crawler:
                simple_result = await crawler.arun(url=url, config=minimal_config)
                if simple_result.success:
                    print("=== MINIMAL FALLBACK CONTENT ===")
                    print(simple_result.markdown[:3000] if simple_result.markdown else "No markdown content")
                else:
                    print(f"All crawling methods failed: {{simple_result.error_message}}")
        except Exception as fallback_error:
            print(f"Complete crawling failure: {{fallback_error}}")

# Run the async crawl with proper event loop handling
try:
    loop = asyncio.get_event_loop()
    if loop.is_running():
        # If already in a running loop, create a task
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(asyncio.run, crawl_site())
            future.result()
    else:
        # If no loop is running, use asyncio.run
        asyncio.run(crawl_site())
except RuntimeError:
    # Fallback if event loop issues persist
    import concurrent.futures
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(asyncio.run, crawl_site())
        future.result()
"""
            
            execution = sandbox.run_code(crawl_code)
            
            if execution.error:
                return f"Crawling error: {execution.error}"
            
            return execution.text if execution.text else "No content extracted"
            
    except Exception as e:
        return f"Web crawling error: {str(e)}"


def create_crew(task_description: str):
    """
    Create a CrewAI crew with E2B tools
    """
    # Define the agent
    python_executor = Agent(
        role='Python Executor and Advanced Web Researcher',
        goal='Execute Python code, intelligently crawl websites with advanced techniques, and solve complex data analysis tasks',
        backstory='''You are an expert Python programmer and web researcher with access to state-of-the-art crawling tools. 
        
You can:
- Execute Python code safely in isolated sandboxes
- Crawl any website with advanced techniques (CSS selectors, wait conditions, JavaScript handling)
- Handle dynamic content, lazy loading, and complex web structures
- Extract structured data from any type of website
- Combine web data with Python analysis for insights
        
You intelligently choose the right approach for each task and always provide clean, actionable results.''',
        tools=[execute_python, crawl_website],
        llm=LLM(
            model="gpt-4o",
            api_key=os.getenv("OPENAI_API_KEY")
        ),
        verbose=True
    )

    # Define the task
    execute_task = Task(
        description=task_description,
        agent=python_executor,
        expected_output="Complete solution with execution results"
    )

    # Create the crew
    crew = Crew(
        agents=[python_executor],
        tasks=[execute_task],
        verbose=True
    )

    return crew


async def execute_crewai_task(task: str, sandbox_id: str = None) -> dict:
    """
    Execute a task using CrewAI with E2B Code Interpreter
    
    Args:
        task: Task description for CrewAI
        sandbox_id: Optional (not used in simple version)
    
    Returns:
        Execution result
    """
    try:
        logger.info(f"Executing CrewAI task: {task[:100]}...")
        
        # Create crew
        crew = create_crew(task)
        
        # Execute task
        result = crew.kickoff()
        
        logger.info("Task completed successfully")
        return {
            "success": True,
            "result": str(result)
        }
        
    except Exception as e:
        logger.error(f"Error executing task: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }


async def list_active_sandboxes() -> dict:
    """List active sandboxes (simple version - no caching)"""
    return {
        "active_sandboxes": [],
        "count": 0,
        "note": "Simple version uses ephemeral sandboxes"
    }


async def cleanup_sandbox(sandbox_id: str) -> dict:
    """Cleanup sandbox (simple version - auto cleanup)"""
    return {
        "success": True, 
        "message": "Simple version uses auto-cleanup sandboxes"
    }


# Create MCP server
app = Server("e2b-crewai-server")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available MCP tools"""
    return [
        Tool(
            name="execute_crewai_task",
            description="""Execute a task using CrewAI agent with advanced E2B Code Interpreter and intelligent Crawl4AI web crawling.

The CrewAI agent features:
- Secure Python code execution in E2B sandboxes
- Advanced web crawling with CSS selectors and dynamic content handling
- Smart content extraction with fallback mechanisms
- JavaScript execution for dynamic websites
- Intelligent data analysis and processing

Capabilities:
- Mathematical calculations and data analysis
- Website crawling with advanced targeting (CSS selectors, wait conditions)
- Dynamic content handling (lazy loading, AJAX, JavaScript-rendered content)
- Structured data extraction from any website type
- Combined web scraping + data analysis workflows
- Robust error handling with multiple fallback strategies

Examples:
- "Calculate compound interest for a $10000 investment"
- "Crawl a news website and extract headlines with sentiment analysis"
- "Scrape product data from any e-commerce site and analyze pricing trends"
- "Extract social media posts and calculate engagement metrics"
- "Combine multiple website data sources for comprehensive analysis"
- "Handle complex websites with dynamic loading and extract specific content"

The agent intelligently selects the optimal approach for each task.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "task": {
                        "type": "string",
                        "description": "Task description for the CrewAI agent"
                    },
                    "sandbox_id": {
                        "type": "string",
                        "description": "Optional: Not used in simple version"
                    }
                },
                "required": ["task"]
            }
        ),
        Tool(
            name="list_sandboxes",
            description="List active E2B sandboxes (simple version uses ephemeral sandboxes)",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="cleanup_sandbox",
            description="Cleanup sandbox (simple version uses auto-cleanup)",
            inputSchema={
                "type": "object",
                "properties": {
                    "sandbox_id": {
                        "type": "string",
                        "description": "Sandbox ID (not used in simple version)"
                    }
                },
                "required": ["sandbox_id"]
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool calls"""

    if name == "execute_crewai_task":
        task = arguments.get("task")
        sandbox_id = arguments.get("sandbox_id")

        if not task:
            return [TextContent(
                type="text",
                text=json.dumps({"error": "Task parameter is required"})
            )]

        result = await execute_crewai_task(task, sandbox_id)

        return [TextContent(
            type="text",
            text=json.dumps(result, indent=2)
        )]

    elif name == "list_sandboxes":
        result = await list_active_sandboxes()
        return [TextContent(
            type="text",
            text=json.dumps(result, indent=2)
        )]

    elif name == "cleanup_sandbox":
        sandbox_id = arguments.get("sandbox_id", "")
        result = await cleanup_sandbox(sandbox_id)
        return [TextContent(
            type="text",
            text=json.dumps(result, indent=2)
        )]

    else:
        return [TextContent(
            type="text",
            text=json.dumps({"error": f"Unknown tool: {name}"})
        )]


async def main():
    """Run the MCP server"""
    logger.info("Starting E2B CrewAI MCP Server (Simple Version)...")

    # Check required environment variables
    required_vars = ["E2B_API_KEY", "OPENAI_API_KEY"]
    missing = [var for var in required_vars if not os.getenv(var)]

    if missing:
        logger.error(f"Missing required environment variables: {', '.join(missing)}")
        raise Exception(f"Missing environment variables: {', '.join(missing)}")

    logger.info("Environment variables OK")
    logger.info("MCP Server ready to accept connections")

    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())