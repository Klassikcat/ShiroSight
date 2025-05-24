from typing import Any

class CloudWatchError(Exception):
    """Base exception class for CloudWatch related errors."""
    pass

class CloudWatchLogStreamError(CloudWatchError):
    """Exception raised for errors in log stream operations."""
    def __init__(self, stream_name: str, message: str):
        self.stream_name = stream_name
        self.message = message
        super().__init__(f"Error in log stream '{stream_name}': {message}")

class CloudWatchLogGroupError(CloudWatchError):
    """Exception raised for errors in log group operations."""
    def __init__(self, group_name: str, message: str):
        self.group_name = group_name
        self.message = message
        super().__init__(f"Error in log group '{group_name}': {message}")

class CloudWatchPaginationError(CloudWatchError):
    """Exception raised for errors in pagination operations."""
    def __init__(self, message: str):
        self.message = message
        super().__init__(f"Pagination error: {message}")

class CloudWatchTimestampError(CloudWatchError):
    """Exception raised for errors in timestamp validation."""
    def __init__(self, timestamp: Any, message: str):
        self.timestamp = timestamp
        self.message = message
        super().__init__(f"Invalid timestamp '{timestamp}': {message}")
