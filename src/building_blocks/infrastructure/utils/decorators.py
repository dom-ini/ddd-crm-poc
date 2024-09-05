from ast import TypeVar
from functools import wraps
from typing import Any, Callable


def call_method_before(method_name: str, *before_args, **before_kwargs):
    def decorator(method):
        @wraps(method)
        def wrapper(self, *args, **kwargs):
            before_method = getattr(self, method_name)
            before_method(*before_args, **before_kwargs)
            return method(self, *args, **kwargs)

        return wrapper

    return decorator
