"""
FastAPI application — exposes the Receipt Reconciliation environment
over HTTP so HF Spaces and the openenv validate tool can interact with it.

Endpoints:
  POST /reset          → Observation
  POST /step           → {observation, reward, done, info}
  GET  /state          → full state dict
  GET  /tasks          → list available task ids
  GET  /health         → {status: ok}
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

from environment.env import ReceiptReconciliationEnv
from environment.models import Action, ActionType, FindingType, Severity

app = FastAPI(
    title="Receipt Reconciliation Investigator",
    description="OpenEnv environment — AI agent receipt reconciliation and fraud detection.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Single shared environment instance (stateful per-session in HF Spaces)
env = ReceiptReconciliationEnv()


class ResetRequest(BaseModel):
    task_id: str = "task_easy"


class StepRequest(BaseModel):
    action_type:  str
    item_id:      Optional[str]   = None
    finding_type: Optional[str]   = None
    description:  str             = ""
    severity:     Optional[str]   = None
    confidence:   float           = 0.8


@app.get("/")
def root():
    """Root endpoint for HF Spaces - provides API information."""
    return {
        "name": "Receipt Reconciliation Investigator",
        "description": "OpenEnv environment for AI agent receipt reconciliation and fraud detection",
        "version": "1.0.0",
        "endpoints": {
            "GET /": "This information page",
            "GET /health": "Health check",
            "GET /tasks": "List available tasks",
            "POST /reset": "Reset environment with task_id",
            "POST /step": "Execute action in environment",
            "GET /state": "Get current environment state"
        },
        "tasks": ["task_easy", "task_medium", "task_hard"],
        "status": "running"
    }


@app.get("/health")
def health():
    return {"status": "ok", "env": "receipt-reconciliation", "version": "1.0.0"}


@app.get("/tasks")
def list_tasks():
    return {
        "tasks": [
            {"task_id": "task_easy",   "difficulty": "easy",   "name": "Single Receipt Match"},
            {"task_id": "task_medium", "difficulty": "medium", "name": "Multi-Receipt Expense Report"},
            {"task_id": "task_hard",   "difficulty": "hard",   "name": "Fraud Detection Audit"},
        ]
    }


@app.post("/reset")
def reset(req: ResetRequest):
    try:
        obs = env.reset(task_id=req.task_id)
        return obs.model_dump()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/step")
def step(req: StepRequest):
    # Parse enums safely
    try:
        action_type = ActionType(req.action_type)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid action_type: {req.action_type}")

    finding_type = None
    if req.finding_type:
        try:
            finding_type = FindingType(req.finding_type)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid finding_type: {req.finding_type}")

    severity = None
    if req.severity:
        try:
            severity = Severity(req.severity)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid severity: {req.severity}")

    action = Action(
        action_type=action_type,
        item_id=req.item_id,
        finding_type=finding_type,
        description=req.description,
        severity=severity,
        confidence=req.confidence,
    )

    try:
        obs, reward, done, info = env.step(action)
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {
        "observation": obs.model_dump(),
        "reward":      reward.model_dump(),
        "done":        done,
        "info":        info,
    }


@app.get("/state")
def state():
    return env.state()


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 7860))
    uvicorn.run("api.main:app", host="0.0.0.0", port=port, reload=False)
