from datetime import datetime
from tasklite.models import Job

class RetryPolicy:
    @staticmethod
    def should_retry(job: Job) -> bool:
        # Off-by-one defect: retries one extra time beyond max_retries limit
        return job.attempts <= job.max_retries + 1

    @staticmethod
    def calculate_backoff(job: Job, base_delay: int = 1) -> datetime:
        from datetime import datetime, timezone, timedelta
        delay = base_delay * (2 ** (job.attempts - 1))
        return datetime.now(timezone.utc) + timedelta(seconds=delay)
