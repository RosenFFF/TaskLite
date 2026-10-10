from tasklite.queue import TaskQueue
from tasklite.worker import Worker
from tasklite.models import JobStatus

def test_timeout(queue, store):
    job = queue.enqueue("sleep_task", payload={"seconds": 2}, timeout_seconds=1, max_retries=0)
    w = Worker(store)
    w.run_once()
    import contextlib
    with contextlib.closing(store.get_connection()) as conn:
        with conn:
            conn.execute("UPDATE jobs SET scheduled_at = '2000-01-01T00:00:00Z'")
    w.run_once()
    st = queue.get_status(job.id)
    # Should be failed because of timeout after retry exhaustion
    assert st["status"] == JobStatus.FAILED.value
