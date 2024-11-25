from typing import Union
import logging
from pyrate_limiter import (BucketFullException, Duration, Limiter,
                            MemoryListBucket, RequestRate)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RateLimiter:

    def __init__(self) -> None:
        """Initializes the RateLimiter with predefined request rates."""
        # Define request rates
        self.second_rate = RequestRate(2, Duration.SECOND)
        self.minute_rate = RequestRate(17, Duration.MINUTE)
        self.hourly_rate = RequestRate(1000, Duration.HOUR)
        self.daily_rate = RequestRate(10000, Duration.DAY)

        # Create the Limiter
        self.limiter = Limiter(
            self.minute_rate,
            self.hourly_rate,
            self.daily_rate,
            bucket_class=MemoryListBucket,
        )

    async def acquire(self, userid: Union[int, str]) -> bool:
        """Attempts to acquire permission to make a request for the given user ID.
        
        Args:
            userid (Union[int, str]): The user ID for which the rate limit is checked.

        Returns:
            bool: True if the request is rate limited, False if allowed.
        """
        try:
            # Try to acquire the request permission
            if self.limiter.try_acquire(userid):
                logger.info(f"Request allowed for user {userid}.")
                return False  # Allowed
            else:
                logger.warning(f"Rate limit exceeded for user {userid}.")
                return True  # Rate limited
        except BucketFullException:
            logger.error(f"Bucket is full for user {userid}. Request denied.")
            return True  # Rate limited
