import logging
import time
from functools import wraps

logger = logging.getLogger(__name__)


def time_logger(func):
    """Decorator that logs the execution time of a function. Debug only."""

    @wraps(func)
    def wrapper(*args, **kw):
        start_time = time.time()
        result = func(*args, **kw)
        end_time = time.time()
        elapsed_time = end_time - start_time
        logging.info(f"Function '{func.__name__}' took {elapsed_time:.4f} seconds")
        return result

    return wrapper
