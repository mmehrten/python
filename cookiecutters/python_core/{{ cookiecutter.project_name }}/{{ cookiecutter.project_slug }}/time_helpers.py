import time


def timestamp_millis() -> int:
    """Returns the current time in milliseconds."""
    return int(time.time() * 1_000)
