import asyncio
from itertools import chain
from typing import Optional, List, Dict, Any, TypedDict
import aioboto3
from mypy_boto3_logs.client import CloudWatchLogsClient
import logging

try:
    from ShiroSightUtilities.timestamps import parse_timestamp
    from ShiroSightUtilities.circuit_breaker import circuit_breaker
except ImportError:  # For Local Development
    from ..ShiroSightUtilities.timestamps import parse_timestamp
    from ..ShiroSightUtilities.circuit_breaker import circuit_breaker

# Constants
DEFAULT_MAX_CONCURRENT_REQUESTS = 10
DEFAULT_MAX_ATTEMPTS = 100
DEFAULT_TIMEOUT = 30

# Type definitions
class LogStream(TypedDict):
    logStreamName: str
    lastEventTime: int

class LogEvent(TypedDict):
    timestamp: int
    message: str
    eventId: str

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


class CloudwatchCollector:
    """A class to collect logs from AWS CloudWatch Logs.
    
    This class provides methods to fetch and process logs from CloudWatch Logs
    with support for pagination, concurrent requests, and error handling.
    """

    def __init__(self, profile_name: Optional[str] = None, max_concurrent_requests: int = DEFAULT_MAX_CONCURRENT_REQUESTS):
        """Initialize the CloudwatchCollector.
        
        Args:
            profile_name: AWS profile name to use for authentication.
                          For production use, set to None, then use IAM Role or Instance Profile.
                          Using IAM Access Key is not supported.
            max_concurrent_requests: Maximum number of concurrent API requests
        """
        self.session = aioboto3.Session(profile_name=profile_name)
        self.semaphore = asyncio.Semaphore(max_concurrent_requests)

    @circuit_breaker(
        max_attempts=DEFAULT_MAX_ATTEMPTS,
        timeout=DEFAULT_TIMEOUT,
        error_message="Failed to fetch log streams"
    )
    async def _fetch_log_streams_page(
        self,
        client: CloudWatchLogsClient,
        log_group_name: str,
        next_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """Fetch a single page of log streams.
        
        Args:
            client: CloudWatch Logs client
            log_group_name: Name of the log group
            next_token: Token for pagination
            
        Returns:
            Dictionary containing log streams and pagination token
        """
        params = {
            "logGroupName": log_group_name,
            "orderBy": "LastEventTime",
            "descending": True,
        }
        if next_token:
            params["nextToken"] = next_token
            
        return await client.describe_log_streams(**params)

    async def get_log_stream_names(self, log_group_name: str) -> List[str]:
        """Get all log stream names for a given log group.
        
        Args:
            log_group_name: Name of the log group to fetch streams from
            
        Returns:
            List of log stream names
        """
        log_streams: List[str] = []
        next_token = None
        
        async with self.semaphore:
            async with self.session.client("logs") as client:
                while True:
                    response = await self._fetch_log_streams_page(client, log_group_name, next_token)
                    log_streams.extend([stream["logStreamName"] for stream in response["logStreams"]])
                    next_token = response.get("nextToken")
                    if not next_token or next_token == response.get("nextToken"):
                        break
                        
        return log_streams

    async def _fetch_log_events_page(
        self,
        client: CloudWatchLogsClient,
        log_group_name: str,
        log_stream_name: str,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
        next_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """Fetch a single page of log events from a stream.
        
        Args:
            client: CloudWatch Logs client
            log_group_name: Name of the log group
            log_stream_name: Name of the log stream
            start_time: Start time in milliseconds
            end_time: End time in milliseconds
            next_token: Token for pagination
            
        Returns:
            Dictionary containing log events and pagination token
        """
        params = {
            "logGroupName": log_group_name,
            "logStreamName": log_stream_name,
        }
        if start_time:
            params["startTime"] = start_time
        if end_time:
            params["endTime"] = end_time
        if next_token:
            params["nextToken"] = next_token
            
        return await client.get_log_events(**params)

    async def fetch_log_stream(
        self, 
        log_stream_name: str, 
        log_group_name: str, 
        start_time: Optional[str] = None, 
        end_time: Optional[str] = None
    ) -> List[LogEvent]:
        """Fetch all logs from a single stream with pagination support.
        
        Args:
            log_stream_name: Name of the log stream
            log_group_name: Name of the log group
            start_time: Start time in ISO format
            end_time: End time in ISO format
            
        Returns:
            List of log events
        """
        async with self.semaphore:
            all_events: List[LogEvent] = []
            next_token = None
            
            async with self.session.client("logs") as client:
                while True:
                    try:
                        response = await self._fetch_log_events_page(
                            client,
                            log_group_name,
                            log_stream_name,
                            parse_timestamp(start_time) if start_time else None,
                            parse_timestamp(end_time) if end_time else None,
                            next_token
                        )
                        
                        all_events.extend(response.get("events", []))
                        next_token = response.get("nextForwardToken")
                        
                        if not next_token or next_token == response.get("nextToken"):
                            break
                            
                    except Exception as e:
                        logger.error(f"Error fetching logs from stream {log_stream_name}: {str(e)}")
                        break
                    
            return all_events

    async def get_log_events(
        self,
        log_group_name: str,
        log_stream_names: List[str],
        start_time: Optional[str] = None,
        end_time: Optional[str] = None
    ) -> List[LogEvent]:
        """Fetch logs from multiple streams concurrently.
        
        Args:
            log_group_name: Name of the log group
            log_stream_names: List of log stream names
            start_time: Start time in ISO format
            end_time: End time in ISO format
            
        Returns:
            List of log events from all streams
        """
        tasks = [
            self.fetch_log_stream(stream, log_group_name, start_time, end_time)
            for stream in log_stream_names
        ]
        log_streams = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions and flatten results
        valid_results = [
            result for result in log_streams 
            if not isinstance(result, Exception)
        ]
        return list(chain.from_iterable(valid_results))

    async def collect_logs(
        self, 
        log_group_name: str, 
        start_time: Optional[str] = None, 
        end_time: Optional[str] = None
    ) -> List[LogEvent]:
        """Main method to collect logs from CloudWatch.
        
        Args:
            log_group_name: Name of the log group
            start_time: Start time in ISO format
            end_time: End time in ISO format
            
        Returns:
            List of log events from all streams in the log group
        """
        log_stream_names = await self.get_log_stream_names(log_group_name)
        return await self.get_log_events(
            log_group_name, 
            log_stream_names, 
            start_time, 
            end_time
        )