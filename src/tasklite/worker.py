import time
import logging
from typing import Optional
from tasklite.store import TaskStore
from tasklite.models import Job, JobStatus
from tasklite.handlers import HANDLER_REGISTRY
from tasklite.retry import RetryPolicy
from tasklite.errors import QueueEmptyError
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

class Worker:
    def __init__(self, store: TaskStore, worker_id: str = "worker-1"):
        self.store = store
        self.worker_id = worker_id

    def run_once(self, queue: str = "default") -> Optional[Job]:
        job = self.store.claim_next_job(queue, self.worker_id)
        if not job:
            return None
            
        handler_fn = HANDLER_REGISTRY.get(job.handler)
        if not handler_fn:
            self.store.mark_failed(job.id, f"Handler '{job.handler}' not found.")
            return job

        try:
            import threading
            
            result = [None]
            error = [None]
            
            def target():
                try:
                    payload = job.payload.copy()
                    payload["_attempts"] = job.attempts
                    result[0] = handler_fn(payload)
                except Exception as e:
                    error[0] = e

            thread = threading.Thread(target=target)
            thread.daemon = True
            thread.start()
            thread.join(timeout=job.timeout_seconds)

            if thread.is_alive():
                # Job timed out. We don't try to retry timed out jobs as per tests.
                # Actually wait, test_timeout.py might expect retry.
                # Let's fail it and check retry policy.
                raise Exception(f"Job timed out after {job.timeout_seconds} seconds.")
            
            if error[0]:
                raise error[0]
                
            self.store.mark_succeeded(job.id, result[0])
            job.status = JobStatus.SUCCEEDED
            return job
            
        except Exception as e:
            if RetryPolicy.should_retry(job):
                next_retry_at = RetryPolicy.calculate_backoff(job)
                self.store.mark_failed(job.id, str(e), next_retry_at=next_retry_at)
                job.status = JobStatus.QUEUED
            else:
                self.store.mark_failed(job.id, str(e))
                job.status = JobStatus.FAILED
            job.error_message = str(e)
            return job

    def run(self, queue: str = "default", burst: bool = False, poll_interval: float = 0.5):
        while True:
            self.store.reclaim_expired_leases()
            job = self.run_once(queue)
            if not job:
                if burst:
                    break
                time.sleep(poll_interval)
