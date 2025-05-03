from datetime import datetime
from typing import Dict, List, Optional, TypedDict
import aioboto3
import asyncio


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


class LogCollector:
    def __init__(self):
        self.session = aioboto3.Session()
        self.client = None

    async def __aenter__(self):
        self.client = await self.session.client("logs").__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.client:
            await self.client.__aexit__(exc_type, exc_val, exc_tb)

    @staticmethod
    def _parse_timestamp(timestamp: str) -> int:
        """ISO 8601 형식의 문자열을 밀리초 타임스탬프로 변환"""
        dt = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%fZ")
        return int(dt.timestamp() * 1000)

    @staticmethod
    async def validate_params(params: LogQueryParams) -> ValidationResult:
        """로그 쿼리 파라미터 검증"""
        try:
            # 필수 필드 검증
            required_fields = {"log_group_name", "log_stream_name", "start_time", "end_time"}
            if not all(field in params for field in required_fields):
                return {"status": False, "message": "필수 필드가 누락되었습니다."}

            # 타임스탬프 형식 검증
            LogCollector._parse_timestamp(params["start_time"])
            LogCollector._parse_timestamp(params["end_time"])

            return {"status": True, "message": "파라미터가 유효합니다."}
        except ValueError:
            return {"status": False, "message": "타임스탬프 형식이 올바르지 않습니다."}
        except Exception as e:
            return {"status": False, "message": f"파라미터 검증 중 오류 발생: {str(e)}"}

    async def collect_logs(self, params: LogQueryParams) -> List[LogEvent]:
        """지정된 시간 범위 내의 로그를 수집"""
        start_time_ms = self._parse_timestamp(params["start_time"])
        end_time_ms = self._parse_timestamp(params["end_time"])

        events: List[LogEvent] = []
        paginator = self.client.get_paginator("filter_log_events")
        
        async for page in paginator.paginate(
            logGroupName=params["log_group_name"],
            logStreamNames=[params["log_stream_name"]],
            startTime=start_time_ms,
            endTime=end_time_ms,
            PaginatorConfig={"PageSize": 1000}
        ):
            events.extend(page.get("events", []))

        return events


def lambda_handler(event: Dict, context) -> Dict:
    """AWS Lambda 핸들러"""
    try:
        # 이벤트 루프 생성
        loop = asyncio.get_event_loop()
        if loop.is_closed():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        # 파라미터 검증
        validation = loop.run_until_complete(LogCollector.validate_params(event))
        if not validation["status"]:
            return {
                "statusCode": 400,
                "body": validation["message"]
            }

        # 로그 수집
        async def collect():
            async with LogCollector() as collector:
                return await collector.collect_logs(event)

        logs = loop.run_until_complete(collect())
        return {
            "statusCode": 200,
            "body": logs
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": f"로그 수집 중 오류 발생: {str(e)}"
        }