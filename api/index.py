"""Vercel serverless entrypoint: exposes the dashboard's FastAPI app (dashboard/app.py).

Static files (dashboard/static/, outputs/) are served by Vercel's CDN via the rewrites in
vercel.json; only /api/* reaches this function.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "dashboard"))

from app import app  # noqa: E402,F401
