import pytest
from tasklite.errors import HandlerNotFoundError

def test_enqueue(queue):
    job = queue.enqueue("mock_email", {"to": "a@b.com"})
    assert job.handler == "mock_email"
    assert job.status.value == "queued"

def test_enqueue_invalid_handler(queue):
    with pytest.raises(HandlerNotFoundError):
        queue.enqueue("invalid_handler")

def test_get_status(queue):
    job = queue.enqueue("mock_email")
    st = queue.get_status(job.id)
    assert st["status"] == "queued"

def test_cancel(queue):
    job = queue.enqueue("mock_email")
    queue.cancel_job(job.id)
    st = queue.get_status(job.id)
    assert st["status"] == "cancelled"

def test_priority_ordering(queue, store):
    job_low = queue.enqueue("mock_email", priority="low")
    job_high = queue.enqueue("mock_email", priority="high")
    job_normal = queue.enqueue("mock_email", priority="normal")
    
    first = store.claim_next_job("default", "worker_1")
    second = store.claim_next_job("default", "worker_1")
    third = store.claim_next_job("default", "worker_1")
    
    assert first.id == job_high.id
    assert second.id == job_normal.id
    assert third.id == job_low.id

def test_fifo_ordering_same_priority(queue, store):
    job1 = queue.enqueue("mock_email", priority="normal")
    job2 = queue.enqueue("mock_email", priority="normal")
    
    first = store.claim_next_job("default", "worker_1")
    second = store.claim_next_job("default", "worker_1")
    
    assert first.id == job1.id
    assert second.id == job2.id
