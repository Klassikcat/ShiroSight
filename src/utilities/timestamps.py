
from datetime import datetime


def parse_timestamp(timestamp: str) -> int:
    """ISO 8601 형식의 문자열을 밀리초 타임스탬프로 변환"""
    dt = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%fZ")
    return int(dt.timestamp() * 1000)