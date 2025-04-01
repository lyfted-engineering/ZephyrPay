import uvicorn
import os
import argparse
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

# Parse command line arguments
parser = argparse.ArgumentParser(description="Run the ZephyrPay FastAPI server")
parser.add_argument("--host", default="0.0.0.0", help="Host to bind the server to")
parser.add_argument("--port", type=int, default=8000, help="Port to bind the server to")
parser.add_argument("--reload", action="store_true", help="Enable auto-reload for development")
parser.add_argument("--workers", type=int, default=1, help="Number of worker processes")
parser.add_argument("--log-level", default="info", help="Logging level")
args = parser.parse_args()

if __name__ == "__main__":
    # Run the FastAPI application with uvicorn
    uvicorn.run(
        "backend.app.main:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        workers=args.workers,
        log_level=args.log_level
    )
