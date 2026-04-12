from typing import Any, Dict, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from env.inbox_env import InboxEnv

app = FastAPI(title="Email Declutter OpenEnv API", version="1.0.0")

# Single shared environment instance for hackathon evaluation
env = InboxEnv()
initialized = False


class ResetRequest(BaseModel):
    seed: Optional[int] = None


class StepRequest(BaseModel):
    type: str = Field(..., description="archive | flag | reply | delete")
    template: Optional[str] = Field(default=None, description="none | ack | escalate | schedule")


@app.get("/")
def root() -> Dict[str, Any]:
    return {
        "message": "Email Declutter OpenEnv API is running",
        "endpoints": ["/reset", "/step", "/state", "/health"]
    }


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.post("/reset")
def reset(request: Optional[ResetRequest] = None) -> Dict[str, Any]:
    global initialized

    seed = request.seed if request else None
    observation = env.reset(seed=seed)
    initialized = True

    return {
        "observation": observation,
        "done": False,
        "info": {
            "message": "Environment reset successfully"
        }
    }


@app.post("/step")
def step(request: StepRequest) -> Dict[str, Any]:
    global initialized

    if not initialized:
        # Auto-reset so evaluator does not fail just because step came first
        env.reset()
        initialized = True

    action = {"type": request.type}
    if request.template is not None:
        action["template"] = request.template

    try:
        observation, reward, done, info = env.step(action)
        return {
            "observation": observation,
            "reward": reward,
            "done": done,
            "info": info
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/state")
def state() -> Dict[str, Any]:
    global initialized

    if not initialized:
        observation = env.reset()
        initialized = True
        return {
            "initialized": True,
            "state": env.state(),
            "observation": observation
        }

    return {
        "initialized": True,
        "state": env.state()
    }


@app.get("/grade")
def grade() -> Dict[str, Any]:
    global initialized

    if not initialized:
        env.reset()
        initialized = True

    return env.grade_episode()

def server():
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=7860)