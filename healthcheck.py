"""
FastAPI health check and metrics endpoint for VPS monitoring.
"""
from fastapi import FastAPI
from sandbox_pool import get_sandbox_pool
import logging

app = FastAPI(title="CrewAI E2B Health Check")
logger = logging.getLogger(__name__)


@app.get("/health")
def health_check():
    """
    Health check endpoint for monitoring systems.

    Returns:
        Health status with sandbox availability
    """
    try:
        pool = get_sandbox_pool()
        status = pool.get_health_status()
        return status
    except Exception as e:
        logger.exception("Health check failed")
        return {
            "status": "error",
            "error": str(e)
        }


@app.get("/metrics")
def get_metrics():
    """
    Detailed metrics endpoint for monitoring.

    Returns:
        Comprehensive metrics including E2B usage
    """
    try:
        pool = get_sandbox_pool()
        return pool.get_metrics()
    except Exception as e:
        logger.exception("Metrics retrieval failed")
        return {
            "error": str(e)
        }


@app.get("/")
def root():
    """Root endpoint."""
    return {
        "service": "CrewAI E2B Code Executor",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "metrics": "/metrics"
        }
    }
