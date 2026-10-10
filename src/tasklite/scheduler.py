from datetime import datetime, timezone
import dateutil.parser
from tasklite.queue import TaskQueue
from tasklite.models import Job

def parse_iso_datetime(dt_str: str) -> datetime:
    dt = dateutil.parser.isoparse(dt_str)
    if dt.tzinfo is None:
        raise ValueError("Naive datetime is not allowed. Must include timezone offset.")
    return dt.astimezone(timezone.utc)

def schedule_job(queue: TaskQueue, handler: str, scheduled_at_str: str, **kwargs) -> Job:
    dt = parse_iso_datetime(scheduled_at_str)
    now = datetime.now(timezone.utc)
    delay_seconds = max(0, int((dt - now).total_seconds()))
    kwargs['delay_seconds'] = delay_seconds
    return queue.enqueue(handler, **kwargs)
