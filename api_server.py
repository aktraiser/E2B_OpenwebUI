"""
FastAPI Server pour E2B CrewAI
Expose les tools via HTTP REST pour OpenWebUI
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import os
import logging
from dotenv import load_dotenv

# Import la logique MCP existante
from mcp_server import (
    execute_crewai_task,
    list_active_sandboxes,
    cleanup_sandbox
)

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("e2b-crewai-api")

# Create FastAPI app
app = FastAPI(
    title="E2B CrewAI API",
    description="Execute tasks using CrewAI agents in E2B sandboxes with MCP tools",
    version="1.0.0"
)

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request models
class TaskRequest(BaseModel):
    task: str
    sandbox_id: Optional[str] = None


class CleanupRequest(BaseModel):
    sandbox_id: str


# Endpoints
@app.get("/")
def root():
    return {
        "service": "E2B CrewAI API",
        "status": "running",
        "docs": "/docs"
    }


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/execute_crewai_task")
async def api_execute_task(request: TaskRequest):
    """
    Execute a task using CrewAI agent in E2B sandbox

    The agent has access to:
    - Python code execution
    - Web search via Browserbase/DuckDuckGo
    - Academic research via ArXiv
    - More MCP tools
    """
    try:
        logger.info(f"Executing task: {request.task[:100]}...")

        result = await execute_crewai_task(
            task=request.task,
            sandbox_id=request.sandbox_id
        )

        logger.info(f"Task completed: {result.get('success', False)}")
        return result

    except Exception as e:
        logger.error(f"Task execution failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/list_sandboxes")
async def api_list_sandboxes():
    """List all active E2B sandboxes"""
    try:
        result = await list_active_sandboxes()
        return result
    except Exception as e:
        logger.error(f"Failed to list sandboxes: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/cleanup_sandbox/{sandbox_id}")
async def api_cleanup_sandbox(sandbox_id: str):
    """Remove a sandbox from cache"""
    try:
        result = await cleanup_sandbox(sandbox_id)
        return result
    except Exception as e:
        logger.error(f"Failed to cleanup sandbox: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    # Check environment variables
    required_vars = ["E2B_API_KEY", "OPENAI_API_KEY"]
    missing = [var for var in required_vars if not os.getenv(var)]

    if missing:
        logger.error(f"Missing environment variables: {', '.join(missing)}")
        raise Exception(f"Missing required environment variables: {', '.join(missing)}")

    logger.info("Starting E2B CrewAI API server...")
    logger.info("API documentation available at: http://0.0.0.0:8000/docs")

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
