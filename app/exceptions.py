class EventManagementError(Exception):
    """Base exception for Event Management errors"""
    pass

class EventValidationError(EventManagementError):
    """Raised when event data fails validation rules"""
    pass

class EventNotFoundError(EventManagementError):
    """Raised when an event cannot be found"""
    pass

class EventOperationError(EventManagementError):
    """Raised when a database operation fails (e.g. deletion with active registrations)"""
    pass
