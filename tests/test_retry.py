from tasklite.retry import RetryPolicy
from tasklite.queue import TaskQueue
from tasklite.worker import Worker
from tasklite.models import JobStatus

def test_retry_policy(queue, store):
    job = queue.enqueue("failing_task", max_retries=2)
    w = Worker(store)
    
    # Attempt 1
    w.run_once()
    st = queue.get_status(job.id)
    assert st["status"] == JobStatus.QUEUED.value
    assert st["attempts"] == 1
    
    import contextlib
    with contextlib.closing(store.get_connection()) as conn:
        with conn:
            conn.execute("UPDATE jobs SET scheduled_at = '2000-01-01T00:00:00Z'")
    
    # Attempt 2
    w.run_once()
    st = queue.get_status(job.id)
    assert st["status"] == JobStatus.QUEUED.value
    assert st["attempts"] == 2
