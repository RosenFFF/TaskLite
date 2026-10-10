import time
from typing import Dict, Any

def mock_email(payload: Dict[str, Any]) -> Dict[str, Any]:
    return {"sent": True, "to": payload.get("to")}

def compute_summary(payload: Dict[str, Any]) -> Dict[str, Any]:
    data = payload.get("data", [])
    return {"length": len(data), "sum": sum(data)}

def failing_task(payload: Dict[str, Any]) -> Dict[str, Any]:
    raise RuntimeError("Intentional failure")

def flaky_task(payload: Dict[str, Any]) -> Dict[str, Any]:
    attempts = payload.get("_attempts", 1)
    if attempts >= payload.get("succeed_on_attempt", 2):
        return {"success": True}
    raise RuntimeError("Flaky task failed")

def sleep_task(payload: Dict[str, Any]) -> Dict[str, Any]:
    time.sleep(payload.get("seconds", 1))
    return {"slept": True}

HANDLER_REGISTRY = {
    "mock_email": mock_email,
    "compute_summary": compute_summary,
    "failing_task": failing_task,
    "flaky_task": flaky_task,
    "sleep_task": sleep_task,
}
