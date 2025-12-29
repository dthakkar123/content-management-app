import time
import asyncio
from collections import deque
from typing import Dict


class RateLimiter:
    """
    Token bucket rate limiter for API calls.

    Limits the number of requests that can be made within a time window.
    """

    def __init__(self, max_requests: int, time_window: int):
        """
        Initialize rate limiter.

        Args:
            max_requests: Maximum number of requests allowed
            time_window: Time window in seconds
        """
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests: deque = deque()
        self._lock = asyncio.Lock()

    async def acquire(self):
        """
        Acquire permission to make a request.
        Waits if rate limit would be exceeded.
        """
        async with self._lock:
            current_time = time.time()

            # Remove requests outside the time window
            while self.requests and self.requests[0] <= current_time - self.time_window:
                self.requests.popleft()

            # If at max requests, wait until oldest request expires
            if len(self.requests) >= self.max_requests:
                wait_time = self.time_window - (current_time - self.requests[0])
                if wait_time > 0:
                    await asyncio.sleep(wait_time)
                    # Remove expired requests after waiting
                    current_time = time.time()
                    while self.requests and self.requests[0] <= current_time - self.time_window:
                        self.requests.popleft()

            # Add new request timestamp
            self.requests.append(current_time)

    async def can_proceed(self) -> bool:
        """
        Check if a request can proceed without waiting.

        Returns:
            bool: True if under rate limit
        """
        current_time = time.time()

        # Remove requests outside the time window
        while self.requests and self.requests[0] <= current_time - self.time_window:
            self.requests.popleft()

        return len(self.requests) < self.max_requests


class APIRateLimits:
    """
    Central registry of rate limiters for different APIs.
    """

    _limiters: Dict[str, RateLimiter] = {
        "twitter": RateLimiter(max_requests=100, time_window=900),  # 100 per 15 min
        "claude": RateLimiter(max_requests=50, time_window=60),     # 50 per minute
        "arxiv": RateLimiter(max_requests=3, time_window=1),        # 3 per second
        "general": RateLimiter(max_requests=10, time_window=1),     # 10 per second
    }

    @classmethod
    def get_limiter(cls, api_name: str) -> RateLimiter:
        """
        Get rate limiter for a specific API.

        Args:
            api_name: Name of the API (twitter, claude, arxiv, general)

        Returns:
            RateLimiter instance
        """
        return cls._limiters.get(api_name, cls._limiters["general"])
