"""
FastAPI REST API for CrewAI task execution
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from crew import CodeExecutionCrewVPS
from sandbox_pool import get_sandbox_pool
from healthcheck import app as health_app
import logging

logger = logging.getLogger(__name__)

app = FastAPI(
    title="CrewAI E2B Code Executor API",
    description="Execute Python code tasks via CrewAI agents"
)

# Include health endpoints
app.mount("/health", health_app, name="health")

@app.get("/health")
async def health():
    """Health check endpoint"""
    pool = get_sandbox_pool()
    metrics = pool.get_metrics()
    
    return {
        "status": "healthy",
        "can_create_sandbox": True,
        "reason": "OK",
        "active_sandboxes": metrics.get("active_sandboxes", 0),
        "hourly_usage": f"{metrics.get('hourly_count', 0)}/{metrics.get('config', {}).get('max_sandboxes_per_hour', 20)}",
        "failure_rate": f"{(metrics.get('total_failed', 0) / max(1, metrics.get('total_created', 1)) * 100):.1f}%",
        "avg_execution_time": f"{metrics.get('avg_execution_time', 0):.2f}s"
    }

@app.get("/metrics")
async def metrics():
    """Get sandbox pool metrics"""
    pool = get_sandbox_pool()
    return pool.get_metrics()

class TaskRequest(BaseModel):
    task: str

class TaskResponse(BaseModel):
    result: str
    metrics: dict

@app.post("/execute", response_model=TaskResponse)
async def execute_task(request: TaskRequest):
    """Execute a custom task"""
    try:
        logger.info(f"Executing custom task: {request.task[:100]}...")
        
        # Create crew instance with custom task
        crew_instance = CodeExecutionCrewVPS()
        crew_instance.set_custom_task(request.task)
        
        result = crew_instance.crew().kickoff()
        
        # Get current metrics
        pool = get_sandbox_pool()
        metrics = pool.get_metrics()
        
        return TaskResponse(
            result=str(result),
            metrics=metrics
        )
    except Exception as e:
        logger.error(f"Task execution failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {
        "service": "CrewAI E2B Code Executor API", 
        "status": "running",
        "endpoints": {
            "execute": "/execute (POST)",
            "health": "/health",
            "metrics": "/metrics",
            "docs": "/docs"
        }
    }