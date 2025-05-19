import asyncio
import aioboto3


class AthenaLogsCollector:
    def __init__(self, profile_name: str, max_concurrent_requests: int = 10):
        self.session = aioboto3.Session(profile_name=profile_name)
        self.client = self.session.client("athena")
        self.semaphore = asyncio.Semaphore(max_concurrent_requests)
        
        