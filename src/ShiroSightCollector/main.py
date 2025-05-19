import logging
import asyncio
from .cloudwatch import CloudwatchCollector
from .athena import AthenaLogsCollector
from .upload import S3Uploader
from typing import Optional


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


class ShiroSightRunner:
    def __init__(
            self,
            profile_name: str,
            max_concurrent_requests: int = 10,
            collect_athena_logs: bool = True,
            athena_s3_bucket: Optional[str] = None,
            athena_s3_prefix: Optional[str] = None,
            collected_logs_s3_bucket: Optional[str] = None,
            ):
        self.cloudwatch_collector = CloudwatchCollector(profile_name, max_concurrent_requests)
        if collect_athena_logs:
            self.athena_collector = AthenaLogsCollector(profile_name, max_concurrent_requests)
        else:
            self.athena_collector = None
        self.s3_uploader = S3Uploader(profile_name)

    def __post_init__(self):
        required_athena_params = {
            'athena_s3_bucket': self.athena_s3_bucket,
            'athena_s3_prefix': self.athena_s3_prefix
        }
        
        if self.collect_athena_logs:
            missing_params = [param for param, value in required_athena_params.items() 
                            if not value]
            if missing_params:
                raise ValueError(
                    f"The following parameters are required when collect_athena_logs is True: "
                    f"{', '.join(missing_params)}"
                )

    async def run(
            self,
            log_group_name: str,
            start_time: Optional[str] = None,
            end_time: Optional[str] = None
            ):
        tasks = [
            self.cloudwatch_collector.collect_logs(log_group_name, start_time, end_time),
            self.athena_collector.collect_logs(log_group_name, start_time, end_time),
            self.s3_uploader.upload_logs(log_group_name, start_time, end_time)
        ]
        cloudwatch_logs, athena_logs, s3_logs = await asyncio.gather(*tasks)
        return cloudwatch_logs, athena_logs, s3_logs