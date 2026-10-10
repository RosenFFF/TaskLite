"""Sample pipeline demonstration using TaskLite programmatically."""
import time
from tasklite.store import TaskStore
from tasklite.queue import TaskQueue
from tasklite.worker import Worker

def main():
    store = TaskStore("pipeline.db")
    queue = TaskQueue(store)

    print("1. Enqueuing jobs...")
    j1 = queue.enqueue("mock_email", {"to": "alice@example.invalid", "subject": "Hello"}, priority="normal")
    j2 = queue.enqueue("compute_summary", {"items": [10, 20, 30]}, priority="high")
    j3 = queue.enqueue("flaky_task", {"succeed_on_attempt": 2}, max_retries=3, priority="low")

    print(f"Enqueued: {j1.id} (normal), {j2.id} (high), {j3.id} (low)")

    print("\n2. Worker running in burst mode...")
    worker = Worker(store)
    worker.run(burst=True)

    print("\n3. Inspecting completed statuses:")
    for j in [j1, j2, j3]:
        st = queue.get_status(j.id)
        print(f"Job {j.id}: status={st['status']}, attempts={st['attempts']}")

if __name__ == "__main__":
    main()
