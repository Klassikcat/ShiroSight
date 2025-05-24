from dataclasses import dataclass
from datetime import datetime, timezone
import re
from .exceptions import CloudWatchTimestampError


@dataclass
class BaseDataclass:
    def validate_timestamps(self, *timestamp_fields: str):
        for field in timestamp_fields:
            timestamp_ms = getattr(self, field)
            if not isinstance(timestamp_ms, int):
                raise CloudWatchTimestampError(
                    timestamp_ms,
                    f"Timestamp must be an integer (milliseconds since epoch)."
                )
            try:
                # Convert milliseconds to seconds for fromtimestamp
                dt = datetime.fromtimestamp(timestamp_ms / 1000, tz=timezone.utc)
                # Format to ISO 8601 with milliseconds
                iso_format = dt.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
                # Validate ISO 8601 format more strictly for CloudWatch timestamps (milliseconds)
                if not re.match(
                    r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z$',
                    iso_format
                ):
                    raise CloudWatchTimestampError(
                        getattr(self, field),
                        f"Invalid ISO 8601 format with milliseconds: {iso_format}"
                    )
            except (ValueError, OSError) as e:
                raise CloudWatchTimestampError(
                    getattr(self, field),
                    f"Failed to convert timestamp to ISO 8601: {str(e)}"
                )


# Type definitions
@dataclass
class LogStream(BaseDataclass):
    logStreamName: str
    lastEventTime: int # Milliseconds since epoch

    def __post_init__(self):
        self.validate_timestamps('lastEventTime')


@dataclass
class LogEvent(BaseDataclass):
    timestamp: int # Milliseconds since epoch
    message: str
    eventId: str

    def __post_init__(self):
        self.validate_timestamps('timestamp')
