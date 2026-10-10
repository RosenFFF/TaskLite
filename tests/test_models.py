from tasklite.models import Priority, JobStatus
from tasklite.handlers import HANDLER_REGISTRY

def test_priority():
    assert Priority.from_string("high") == Priority.HIGH
    assert Priority.from_string("low") == Priority.LOW
    assert Priority.from_string("normal") == Priority.NORMAL
    assert Priority.from_string("unknown") == Priority.NORMAL

def test_handlers():
    assert "mock_email" in HANDLER_REGISTRY
    assert HANDLER_REGISTRY["mock_email"]({"to": "test@example.com"}) == {"sent": True, "to": "test@example.com"}
