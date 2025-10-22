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
    Advanced web crawler that extracts clean markdown content from websites using modern Crawl4AI.
    
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
    from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
    print("✅ Crawl4AI already available")
except ImportError:
    print("📦 Installing Crawl4AI...")
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-U', 'crawl4ai'])
    print("🔧 Setting up Crawl4AI (this may take a few minutes)...")
    subprocess.check_call(['crawl4ai-setup'])
    print("🎭 Installing Playwright browsers...")
    subprocess.check_call(['playwright', 'install'])
    from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
    print("✅ Crawl4AI setup complete")

import asyncio

async def crawl_site():
    url = "{url}"
    
    print("=== MODERN CRAWL4AI STARTING ===")
    print(f"Target URL: {{url}}")
    
    # Test basic connectivity first
    try:
        import requests
        response = requests.get(url, timeout=10)
        print(f"✅ Basic connectivity: {{response.status_code}} ({{len(response.text)}} chars)")
    except Exception as e:
        print(f"❌ Basic connectivity failed: {{e}}")
    
    # Modern Crawl4AI configuration following documentation examples
    browser_config = BrowserConfig(
        headless=True,
        verbose=True,
        user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    )
    
    run_config = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        word_count_threshold=10,
        page_timeout=30000,
        wait_until="domcontentloaded"
    )
    
    print(f"✅ Modern configs created - Browser: {{browser_config.headless}}, Cache: {{run_config.cache_mode}}")
    
    try:
        async with AsyncWebCrawler(config=browser_config) as crawler:
            print("✅ AsyncWebCrawler initialized")
            
            result = await crawler.arun(
                url=url,
                config=run_config
            )
            
            print("\\n=== CRAWL RESULTS ===")
            print(f"Success: {{result.success}}")
            print(f"Status code: {{getattr(result, 'status_code', 'N/A')}}")
            print(f"Error: {{getattr(result, 'error_message', 'None')}}")
            
            if result.success:
                # Check different content types in modern API
                content = None
                content_type = "none"
                
                if hasattr(result, 'markdown') and result.markdown:
                    if hasattr(result.markdown, 'raw_markdown'):
                        content = result.markdown.raw_markdown
                        content_type = "raw_markdown"
                    elif hasattr(result.markdown, 'fit_markdown'):
                        content = result.markdown.fit_markdown  
                        content_type = "fit_markdown"
                    else:
                        content = str(result.markdown)
                        content_type = "markdown_string"
                elif hasattr(result, 'cleaned_html') and result.cleaned_html:
                    content = result.cleaned_html
                    content_type = "cleaned_html"
                elif hasattr(result, 'html') and result.html:
                    content = result.html[:5000]  # Truncate raw HTML
                    content_type = "raw_html"
                
                print(f"Content type: {{content_type}}")
                print(f"Content length: {{len(content) if content else 0}}")
                
                if content and len(content.strip()) > 50:
                    # Smart truncation for readability
                    if len(content) > 8000:
                        truncate_at = content.find('\\n\\n', 7000)
                        if truncate_at > 0:
                            content = content[:truncate_at] + "\\n\\n[Content truncated...]"
                        else:
                            content = content[:8000] + "\\n[Content truncated...]"
                    
                    print("\\n=== EXTRACTED CONTENT ===")
                    print(f"URL: {{url}}")
                    print(f"Words: {{len(content.split())}}")
                    print("\\n" + content)
                    return content
                else:
                    print("❌ No meaningful content extracted")
                    
                    # Try fallback extraction for news sites
                    if hasattr(result, 'html') and result.html:
                        print("\\n=== FALLBACK: Basic HTML parsing ===")
                        try:
                            from bs4 import BeautifulSoup
                            soup = BeautifulSoup(result.html, 'html.parser')
                            
                            # Common news site selectors
                            headlines = []
                            selectors = [
                                '.titleline a',  # Hacker News
                                'h1, h2, h3',    # Generic headlines
                                '.title',        # Common title class
                                'article h1, article h2'  # Article headlines
                            ]
                            
                            for selector in selectors:
                                elements = soup.select(selector)
                                if elements:
                                    for elem in elements[:10]:
                                        text = elem.get_text().strip()
                                        if len(text) > 10:
                                            headlines.append(text)
                            
                            if headlines:
                                fallback_content = "\\n".join(f"• {{headline}}" for headline in headlines[:15])
                                print(f"Extracted {{len(headlines)}} headlines via fallback")
                                print(fallback_content)
                                return f"Headlines extracted from {{url}}:\\n\\n{{fallback_content}}"
                            else:
                                print("No headlines found with fallback selectors")
                        except Exception as parse_error:
                            print(f"Fallback parsing failed: {{parse_error}}")
            else:
                print(f"❌ Crawl failed: {{result.error_message}}")
                
                # Try simple fallback config
                print("\\n=== SIMPLE FALLBACK ===")
                simple_config = CrawlerRunConfig(
                    cache_mode=CacheMode.BYPASS,
                    word_count_threshold=1,
                    page_timeout=15000
                )
                
                fallback_result = await crawler.arun(url=url, config=simple_config)
                if fallback_result.success:
                    fallback_content = None
                    if hasattr(fallback_result, 'markdown') and fallback_result.markdown:
                        if hasattr(fallback_result.markdown, 'raw_markdown'):
                            fallback_content = fallback_result.markdown.raw_markdown[:3000]
                        else:
                            fallback_content = str(fallback_result.markdown)[:3000]
                    
                    if fallback_content:
                        print(f"Fallback extracted {{len(fallback_content)}} characters")
                        return fallback_content
                
                return f"Failed to crawl {{url}}: {{result.error_message}}"
                
    except Exception as e:
        print(f"Crawling exception: {{e}}")
        return f"Crawling error: {{str(e)}}"

# Execute with proper async handling
try:
    import nest_asyncio
    nest_asyncio.apply()
    result = asyncio.run(crawl_site())
    print("=== FINAL RESULT ===")
    print(result if result else "No content returned")
except Exception as e:
    print(f"Async execution error: {{e}}")
    try:
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(asyncio.run, crawl_site())
            result = future.result(timeout=60)
            print("=== FINAL RESULT (via ThreadPool) ===") 
            print(result if result else "No content returned")
    except Exception as final_error:
        print(f"All execution methods failed: {{final_error}}")
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