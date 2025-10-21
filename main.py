"""
Simple main entry point
"""
import uvicorn
from api import app

if __name__ == "__main__":
    print("🚀 Starting E2B Code Executor")
    uvicorn.run(app, host="0.0.0.0", port=8000)