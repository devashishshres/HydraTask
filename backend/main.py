"""
FastAPI entry point for HydraTask.

Endpoints:
  GET  /           — health check
  POST /hydrate    — takes a vague task, returns a structured action card
"""

import os
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from database import get_db
from schemas import HydrateRequest, ActionCard
from hydrator import hydrate_task

app = FastAPI(title="HydraTask API")

# Allow the Next.js frontend to call this API
# ALLOWED_ORIGINS env var is a comma-separated list; falls back to localhost for local dev
_raw_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000")
_allowed_origins = [o.strip() for o in _raw_origins.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def health_check():
    return {"status": "HydraTask backend is running"}


@app.post("/hydrate", response_model=ActionCard)
def hydrate(request: HydrateRequest, db: Session = Depends(get_db)):
    """Accept a vague task and return an enriched action card."""
    if not request.task.strip():
        raise HTTPException(status_code=400, detail="Task cannot be empty")

    try:
        return hydrate_task(request.task, db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Hydration failed: {str(e)}")
