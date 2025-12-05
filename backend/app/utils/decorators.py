"""
decorators.py
-------------
Custom Python decorators used throughout the application for common tasks
like logging function calls, measuring execution time, and caching results.
"""
import time
from functools import wraps
from ..core.logging_config import get_logger
from typing import Callable

# Get a dedicated logger for decorators/utilities
logger = get_logger("app.utils.decorators")


def log_calls(func: Callable) -> Callable:
    """
    Decorator that logs the function's name and arguments upon entry and exit.
    Useful for tracing flow, especially across service boundaries.
    """

    @wraps(func)
    async def async_wrapper(*args, **kwargs):
        # Format arguments nicely for logging
        func_name = func.__name__
        arg_names = func.__code__.co_varnames[:func.__code__.co_argcount]

        # Exclude 'self' or 'cls' from logging arguments
        log_args = {name: value for name, value in zip(arg_names, args) if name not in ('self', 'cls')}
        log_kwargs = kwargs

        logger.info(f"START {func_name} with args={log_args}, kwargs={log_kwargs}")

        try:
            result = await func(*args, **kwargs)
            logger.info(f"END {func_name}. Success.")
            return result
        except Exception as e:
            logger.error(f"END {func_name}. FAILED with error: {e}", exc_info=False)
            raise

    @wraps(func)
    def sync_wrapper(*args, **kwargs):
        # Same logging logic for synchronous functions
        func_name = func.__name__
        arg_names = func.__code__.co_varnames[:func.__code__.co_argcount]
        log_args = {name: value for name, value in zip(arg_names, args) if name not in ('self', 'cls')}
        log_kwargs = kwargs

        logger.info(f"START {func_name} with args={log_args}, kwargs={log_kwargs}")

        try:
            result = func(*args, **kwargs)
            logger.info(f"END {func_name}. Success.")
            return result
        except Exception as e:
            logger.error(f"END {func_name}. FAILED with error: {e}", exc_info=False)
            raise

    # Determine if the function is synchronous or asynchronous
    if iscoroutinefunction(func):
        return async_wrapper
    else:
        return sync_wrapper


# Helper function to check if a function is a coroutine (async)
from inspect import iscoroutinefunction