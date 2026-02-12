"""Polling utilities with exponential backoff for test assertions."""

import time
from typing import Callable, Any, Optional, TypeVar

T = TypeVar('T')


def poll_until(
    getter: Callable[[], T],
    condition: Callable[[T], bool],
    timeout: int = 300,
    interval: int = 5,
    description: str = "condition"
) -> T:
    """Poll until condition is met or timeout.

    Args:
        getter: Function that returns a value to check
        condition: Function that validates the value (returns True if valid)
        timeout: Maximum time to wait in seconds (default: 300s = 5 minutes)
        interval: Time between polls in seconds (default: 5s)
        description: Human-readable description for error messages

    Returns:
        The value from getter when condition is met

    Raises:
        TimeoutError: If condition not met within timeout

    Example:
        # Wait for table to have >= 28000 records
        count = poll_until(
            lambda: get_record_count("ride_requests"),
            lambda count: count >= 28000,
            timeout=600,
            interval=30,
            description="ride_requests count >= 28,000"
        )
    """
    start_time = time.time()
    attempt = 0

    while True:
        attempt += 1
        elapsed = time.time() - start_time

        try:
            value = getter()

            if condition(value):
                return value

            # Condition not met yet
            if elapsed >= timeout:
                raise TimeoutError(
                    f"Timeout waiting for {description} after {elapsed:.1f}s "
                    f"({attempt} attempts). Last value: {value}"
                )

            # Wait before next attempt
            time.sleep(interval)

        except Exception as e:
            # Re-raise TimeoutError as-is
            if isinstance(e, TimeoutError):
                raise

            # For other errors, check if we should retry
            if elapsed >= timeout:
                raise TimeoutError(
                    f"Error polling for {description} after {elapsed:.1f}s: {e}"
                )

            # Wait before retry
            time.sleep(interval)


def poll_with_exponential_backoff(
    getter: Callable[[], T],
    condition: Callable[[T], bool],
    max_retries: int = 5,
    initial_delay: int = 5,
    description: str = "condition"
) -> T:
    """Poll with exponential backoff (similar to AWS credential propagation pattern).

    Args:
        getter: Function that returns a value to check
        condition: Function that validates the value (returns True if valid)
        max_retries: Maximum number of attempts (default: 5)
        initial_delay: Initial delay in seconds, doubles each retry (default: 5s)
        description: Human-readable description for error messages

    Returns:
        The value from getter when condition is met

    Raises:
        TimeoutError: If condition not met after max_retries

    Example:
        # Wait for workshop keys with exponential backoff
        result = poll_with_exponential_backoff(
            lambda: check_api_keys_file(),
            lambda exists: exists is True,
            max_retries=3,
            description="API-KEYS-AWS.md exists"
        )
    """
    for attempt in range(max_retries):
        try:
            value = getter()

            if condition(value):
                return value

            # Condition not met, retry if not last attempt
            if attempt < max_retries - 1:
                wait_time = initial_delay * (2 ** attempt)
                time.sleep(wait_time)

        except Exception as e:
            # On last attempt, raise the error
            if attempt >= max_retries - 1:
                raise TimeoutError(
                    f"Failed {description} after {max_retries} attempts: {e}"
                )

            # Wait before retry
            wait_time = initial_delay * (2 ** attempt)
            time.sleep(wait_time)

    # All retries exhausted
    raise TimeoutError(
        f"Timeout waiting for {description} after {max_retries} attempts"
    )
