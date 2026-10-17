"""Vercel Serverless Function entry point for CSIC FastAPI backend."""
import sys
from pathlib import Path

# Ensure the repository root directory is present in sys.path
# This allows all existing absolute imports ('from backend.app.*') to resolve cleanly
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Import the pre-configured FastAPI application instance
from backend.app.main import app

# Expose app for Vercel's ASGI runtime handler
__all__ = ["app"]
