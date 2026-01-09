import time
from typing import Callable, Any


class CircuitBreakerOpen(Exception):
    """Raised when circuit breaker is open."""


class CircuitBreaker:
    """
    Simple circuit breaker implementation.
    """

    def __init__(
        self,
        failure_threshold: int = 3,
        recovery_timeout: int = 30,
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout

        self.failure_count = 0
        self.last_failure_time = None
        self.state = "closed"  # closed | open | half_open

    def call(self, func: Callable[..., Any], *args, **kwargs) -> Any:
        now = time.time()

        # -------------------------
        # OPEN → check timeout
        # -------------------------
        if self.state == "open":
            if now - self.last_failure_time >= self.recovery_timeout:
                self.state = "half_open"
            else:
                raise CircuitBreakerOpen("Circuit breaker is open")

        try:
            result = func(*args, **kwargs)

            # Success path
            self.failure_count = 0
            self.state = "closed"
            return result

        except Exception:
            self.failure_count += 1
            self.last_failure_time = time.time()

            # Transition to OPEN
            if self.failure_count >= self.failure_threshold:
                self.state = "open"

            raise
