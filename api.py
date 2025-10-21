"""
Simple FastAPI for E2B code execution
"""
from fastapi import FastAPI
from pydantic import BaseModel
from crew import create_crew

app = FastAPI(title="E2B Code Executor")

class TaskRequest(BaseModel):
    task: str

@app.get("/")
def root():
    return {"status": "running", "service": "E2B Code Executor"}

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.post("/execute")
def execute_task(request: TaskRequest):
    """Execute a task with CrewAI + E2B"""
    try:
        crew = create_crew(request.task)
        result = crew.kickoff()
        return {"result": str(result)}
    except Exception as e:
        return {"error": str(e)}