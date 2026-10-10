from tasklite.store import TaskStore
from tasklite.models import Job, JobStatus, Priority
from datetime import datetime, timezone

def test_store_init(temp_db):
    store = TaskStore(db_path=temp_db)
    # just check initialization doesn't throw
    assert store is not None

def test_claim_next_job(store):
    from tasklite.queue import TaskQueue
    q = TaskQueue(store)
    job1 = q.enqueue("mock_email", priority="low")
    job2 = q.enqueue("mock_email", priority="high")
    
    claimed = store.claim_next_job("default", "w1")
    assert claimed.id == job2.id
    assert claimed.status == JobStatus.RUNNING

def test_reclaim_expired_leases(store):
    from tasklite.queue import TaskQueue
    q = TaskQueue(store)
    q.enqueue("mock_email")
    store.claim_next_job("default", "w1", lease_duration_seconds=-1) # Already expired
    count = store.reclaim_expired_leases()
    assert count == 1
