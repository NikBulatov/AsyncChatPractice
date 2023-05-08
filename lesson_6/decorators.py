import inspect
import sys
import logging
from builtins import callable
from functools import wraps

if sys.argv[0].find("client") == -1:
    LOGGER = logging.getLogger("server")
else:
    LOGGER = logging.getLogger("client")


def log(func: callable) -> callable:
    """
    Decorator for logging when and where decorated function was called
    :param func: callable
    :return: callable
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        LOGGER.debug(
            f"\"{func.__name__}\" function with arguments {args}, {kwargs} "
            f"was called from \"{inspect.stack()[1][3]}\" function, "
            f"from module {func.__module__}")
        return result

    return wrapper
