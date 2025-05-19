import asyncio
from functools import wraps
from typing import Optional, List, Dict, Any, AsyncGenerator, Callable, TypeVar, Awaitable


T = TypeVar('T')


def circuit_breaker(
    max_attempts: int = 100,
    timeout: int = 30,
    error_message: str = "Operation failed"
) -> Callable[[Callable[..., Awaitable[T]]], Callable[..., Awaitable[T]]]:
    """Circuit breaker decorator for async functions with pagination.
    
    Args:
        max_attempts: Maximum number of pagination attempts
        timeout: Timeout in seconds for each operation
        error_message: Custom error message for failures
        
    Returns:
        Decorated function with circuit breaker functionality
    """
    def decorator(func: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[T]]:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            attempts = 0
            while attempts < max_attempts:
                try:
                    async with asyncio.timeout(timeout):
                        result = await func(*args, **kwargs)
                    return result
                except asyncio.TimeoutError:
                    raise TimeoutError(f"Operation timed out after {timeout} seconds")
                except Exception as e:
                    attempts += 1
                    if attempts >= max_attempts:
                        raise Exception(f"{error_message}: {str(e)}")
                    continue
            raise Exception(f"Maximum number of attempts ({max_attempts}) exceeded")
        return wrapper
    return decorator

