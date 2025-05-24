import pytest
import asyncio
from datetime import datetime, timedelta
from ShiroSightCollector.main import ShiroSightRunner

@pytest.mark.asyncio
async def test_shiro_sight_runner():
    # Initialize the runner with test parameters
    runner = ShiroSightRunner(
        max_concurrent_requests=5,
        collect_athena_logs=False,  # Disable Athena for simple test
        collected_logs_s3_bucket="test-bucket"
    )
    
    # Set time range for last 24 hours
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(hours=24)
    
    # Test log collection
    cloudwatch_logs, athena_logs, s3_logs = await runner.run(
        log_group_name="/test/log/group",
        start_time=start_time.isoformat(),
        end_time=end_time.isoformat()
    )
    
    # Basic assertions
    assert isinstance(cloudwatch_logs, list)
    assert athena_logs is None  # Since we disabled Athena
    assert isinstance(s3_logs, list)

@pytest.mark.asyncio
async def test_shiro_sight_runner_with_athena():
    # Initialize the runner with Athena enabled
    runner = ShiroSightRunner(
        max_concurrent_requests=5,
        collect_athena_logs=True,
        athena_s3_bucket="test-athena-bucket",
        athena_s3_prefix="test/prefix",
        collected_logs_s3_bucket="test-bucket"
    )
    
    # Set time range for last 24 hours
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(hours=24)
    
    # Test log collection
    cloudwatch_logs, athena_logs, s3_logs = await runner.run(
        log_group_name="/test/log/group",
        start_time=start_time.isoformat(),
        end_time=end_time.isoformat()
    )
    
    # Basic assertions
    assert isinstance(cloudwatch_logs, list)
    assert isinstance(athena_logs, list)
    assert isinstance(s3_logs, list)

def test_shiro_sight_runner_initialization():
    # Test initialization with invalid parameters
    with pytest.raises(ValueError):
        ShiroSightRunner(
            collect_athena_logs=True,
            # Missing required Athena parameters
        )
