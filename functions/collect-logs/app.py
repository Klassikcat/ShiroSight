import asyncio
from datetime import datetime
from typing import Optional, List, Dict, TypedDict
import aioboto3
import orjson


class LogEvent(TypedDict):
    timestamp: int
    message: str
    logStreamName: str
    logGroupName: str


class LogQueryParams(TypedDict):
    log_group_name: str
    log_stream_name: str
    start_time: str
    end_time: str


class ValidationResult(TypedDict):
    status: bool
    message: str


session = aioboto3.Session(profile_name="blackcircles")
client = session.client("logs")


def parse_timestamp(timestamp: str) -> int:
    """ISO 8601 형식의 문자열을 밀리초 타임스탬프로 변환"""
    dt = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%fZ")
    return int(dt.timestamp() * 1000)


async def get_log_streams(log_group_name: str) -> List[str]:
    async with session.client("logs") as client:
        response = await client.describe_log_streams(
            logGroupName=log_group_name,
            orderBy="LastEventTime",
            descending=True,
        )
        return [stream["logStreamName"] for stream in response["logStreams"]]


async def get_log_events(
    log_group_name: str, 
    log_stream_names: List[str],
    start_time: Optional[str] = None,
    end_time: Optional[str] = None
) -> List[LogEvent]:
    """로그 이벤트를 조회합니다"""
    async with session.client("logs") as client:
        log_streams = []
        # 시작 시간과 종료 시간이 제공된 경우 추가
        for log_stream_name in log_stream_names:
            params = {
                "logGroupName": log_group_name,
                "logStreamName": log_stream_name,
            }
            if start_time:
                params["startTime"] = parse_timestamp(start_time)
            if end_time:
                params["endTime"] = parse_timestamp(end_time)
            params["logStreamName"] = log_stream_name
            response = await client.get_log_events(**params)
            log_streams.append(response.get("events", []))
    return log_streams


async def parse_log_events(log_events: str) -> List[Dict]:
    with asyncio.TaskGroup() as tg:
        tasks = [parse_log_events(log_event) for log_event in log_events]
        parsed_logs = await asyncio.gather(*tasks)
    return parsed_logs


def lambda_handler(event: Dict, context) -> Dict:
    try:
        loop = asyncio.get_event_loop()
        if loop.is_closed():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        log_groups = loop.run_until_complete(get_log_events(event["log_group_name"], event["log_stream_name"], event["start_time"], event["end_time"]))
        events = loop.run_until_complete(parse_log_events(log_groups))
        return {
            "statusCode": 200,
            "body": events
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "body": f"로그 수집 중 오류 발생: {str(e)}"
        }