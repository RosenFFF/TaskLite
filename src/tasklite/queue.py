import uuid
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any, List

from tasklite.models import Job, JobStatus, Priority
from tasklite.store import TaskStore
from tasklite.errors import JobNotFoundError, HandlerNotFoundError, InvalidStateError

class TaskQueue:
    def __init__(self, store: TaskStore):
        self.store = store

    def enqueue(self, handler: str, payload: Optional[Dict[str, Any]] = None, 
                priority: str = "normal", queue: str = "default", 
                max_retries: int = 2, timeout_seconds: int = 30, 
                delay_seconds: int = 0) -> Job:
        from tasklite.handlers import HANDLER_REGISTRY
        if handler not in HANDLER_REGISTRY:
            raise HandlerNotFoundError(f"Handler '{handler}' not registered.")

        now = datetime.now(timezone.utc)
        scheduled_at = now + timedelta(seconds=delay_seconds)
        
        job = Job(
            id=str(uuid.uuid4()),
            queue=queue,
            handler=handler,
            payload=payload or {},
            status=JobStatus.QUEUED,
            priority=Priority.from_string(priority).value,
            attempts=0,
            max_retries=max_retries,
            timeout_seconds=timeout_seconds,
            error_message=None,
            scheduled_at=scheduled_at,
            created_at=now,
            updated_at=now,
            lease_expires_at=None
        )
        self.store.insert_job(job)
        return job

    def get_status(self, job_id: str) -> Dict[str, Any]:
        job = self.store.get_job(job_id)
        if not job:
            raise JobNotFoundError(f"Job {job_id} not found.")
        return {
            "id": job.id,
            "status": job.status.value,
            "queue": job.queue,
            "handler": job.handler,
            "priority": job.priority,
            "attempts": job.attempts,
            "max_retries": job.max_retries,
            "error_message": job.error_message,
            "created_at": job.created_at.isoformat() if job.created_at else None,
            "updated_at": job.updated_at.isoformat() if job.updated_at else None,
        }

    def retry_job(self, job_id: str) -> Job:
        job = self.store.get_job(job_id)
        if not job:
            raise JobNotFoundError(f"Job {job_id} not found.")
        if job.status != JobStatus.FAILED:
            raise InvalidStateError(f"Job {job_id} is not in failed state.")
        
        now = datetime.now(timezone.utc)
        import contextlib
        with contextlib.closing(self.store.get_connection()) as conn:
            with conn:
                conn.execute('''
                    UPDATE jobs
                    SET status = 'queued', attempts = 0, error_message = NULL,
                        updated_at = ?, scheduled_at = ?, lease_expires_at = NULL
                    WHERE id = ?
                ''', (now.astimezone(timezone.utc).isoformat(), now.astimezone(timezone.utc).isoformat(), job_id))
        return self.store.get_job(job_id)

    def cancel_job(self, job_id: str) -> Job:
        job = self.store.get_job(job_id)
        if not job:
            raise JobNotFoundError(f"Job {job_id} not found.")
        if job.status in (JobStatus.SUCCEEDED, JobStatus.FAILED, JobStatus.CANCELLED):
            raise InvalidStateError(f"Job {job_id} cannot be cancelled from state {job.status.value}.")
        
        self.store.mark_cancelled(job_id)
        return self.store.get_job(job_id)
