import pytest
from datetime import datetime, timezone
from tasklite.scheduler import schedule_job, parse_iso_datetime

def test_parse_iso_datetime():
    dt = parse_iso_datetime("2030-01-01T12:00:00+00:00")
    assert dt.year == 2030
    with pytest.raises(ValueError):
        parse_iso_datetime("2030-01-01T12:00:00") # naive

def test_schedule_job(queue):
    job = schedule_job(queue, "mock_email", "2030-01-01T12:00:00+00:00")
    assert job.scheduled_at > datetime.now(timezone.utc)
