import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional, Dict, Any

class JobStatus(Enum):
    QUEUED = "queued"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"

class Priority(Enum):
    LOW = 1
    NORMAL = 5
    HIGH = 10

    @classmethod
    def from_string(cls, value: str) -> "Priority":
        val = value.lower()
        if val == "low":
            return cls.LOW
        elif val == "high":
            return cls.HIGH
        return cls.NORMAL

@dataclass
class Job:
    id: str
    queue: str
    handler: str
    payload: Dict[str, Any]
    status: JobStatus
    priority: int
    attempts: int
    max_retries: int
    timeout_seconds: int
    error_message: Optional[str]
    scheduled_at: datetime
    created_at: datetime
    updated_at: datetime
    lease_expires_at: Optional[datetime] = None

from .handlers import HANDLER_REGISTRY
