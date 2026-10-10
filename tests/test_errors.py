import pytest
from tasklite.errors import (
    TaskLiteError,
    JobNotFoundError,
    HandlerNotFoundError,
    QueueEmptyError,
    DatabaseError,
    JobTimeoutError,
    InvalidStateError,
)

def test_error_hierarchy():
    for err_cls in [
        JobNotFoundError,
        HandlerNotFoundError,
        QueueEmptyError,
        DatabaseError,
        JobTimeoutError,
        InvalidStateError,
    ]:
        err = err_cls("test error")
        assert isinstance(err, TaskLiteError)
        assert str(err) == "test error"
