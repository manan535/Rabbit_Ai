"""Vercel serverless function entry point – exposes the FastAPI app."""

import sys
import os

# Add the backend package to the Python path so imports like
# `from app.config import ...` resolve correctly.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.main import app  # noqa: E402
