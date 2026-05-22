# utils.py
import re
import functools


def log_action(func):
    """Decorator that logs function calls to stdout."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print(f"[LOG] Called function: {func.__name__}")
        return func(*args, **kwargs)
    return wrapper


def validate_record_time(time_str: str) -> bool:
    """Validate time string against MM:SS:ms pattern using regex.

    Args:
        time_str: Time string to validate (e.g., "01:42:35" or "1:05:00")

    Returns:
        True if format matches, False otherwise
    """
    pattern = r"^\d{1,2}:\d{2}:\d{1,3}$"
    return bool(re.match(pattern, time_str))


def time_to_ms(time_str: str) -> int:
    """Convert MM:SS:ms time string to milliseconds for sorting.

    Args:
        time_str: Time string in MM:SS:ms format

    Returns:
        Integer milliseconds, or 99999999 on parse error (pushes to end)
    """
    try:
        parts = time_str.split(':')
        minutes = int(parts[0])
        seconds = int(parts[1])
        ms = int(parts[2])
        return (minutes * 60 * 1000) + (seconds * 1000) + ms
    except Exception:
        return 99999999  # Push invalid entries to the end of sorted lists