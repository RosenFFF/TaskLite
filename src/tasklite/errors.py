class TaskLiteError(Exception):
    pass

class JobNotFoundError(TaskLiteError):
    pass

class HandlerNotFoundError(TaskLiteError):
    pass

class QueueEmptyError(TaskLiteError):
    pass

class DatabaseError(TaskLiteError):
    pass

class JobTimeoutError(TaskLiteError):
    pass

class InvalidStateError(TaskLiteError):
    pass
