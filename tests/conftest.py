import pytest
import os
import tempfile
from tasklite.store import TaskStore
from tasklite.queue import TaskQueue

@pytest.fixture
def temp_db():
    fd, path = tempfile.mkstemp()
    os.close(fd)
    yield path
    os.remove(path)

@pytest.fixture
def store(temp_db):
    return TaskStore(db_path=temp_db)

@pytest.fixture
def queue(store):
    return TaskQueue(store)
