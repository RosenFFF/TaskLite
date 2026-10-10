from tasklite.queue import TaskQueue
from tasklite.worker import Worker
from tasklite.models import JobStatus

def test_worker_run_once(queue, store):
    job = queue.enqueue("mock_email")
    w = Worker(store)
    w.run_once()
    st = queue.get_status(job.id)
    assert st["status"] == JobStatus.SUCCEEDED.value

def test_worker_burst(queue, store):
    queue.enqueue("mock_email")
    queue.enqueue("mock_email")
    w = Worker(store)
    w.run(burst=True)
    assert len(store.list_jobs(status="succeeded")) == 2

def test_flaky_task(queue, store):
    job = queue.enqueue("flaky_task", max_retries=3)
    w = Worker(store)
    w.run_once() # Attempt 1, fails
    
    st = queue.get_status(job.id)
    assert st["status"] == JobStatus.QUEUED.value
    
    # bypass backoff
    import contextlib
    with contextlib.closing(store.get_connection()) as conn:
        with conn:
            conn.execute("UPDATE jobs SET scheduled_at = '2000-01-01T00:00:00Z'")
        
    w.run_once() # Attempt 2, succeeds
    st = queue.get_status(job.id)
    assert st["status"] == JobStatus.SUCCEEDED.value
