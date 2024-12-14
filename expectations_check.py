from __future__ import annotations

from datetime import datetime

from typing import Callable, TypeVar, Any

FunctionCore = TypeVar("FunctionCore", bound=Callable[..., int])


def validate_result(func: FunctionCore) -> FunctionCore:
    """
    A decorator to validate the output.
    Takes the expected result from the `expected_result` argument of the checked function.
    :param func: The function to be checked. Add an `expected_result` argument with the expected result value.
    :return: The return value of hte checked function
    """
    def wrapper(*args: Any, **kwargs: Any) -> int:
        print()
        expected_result: int | None = kwargs.pop('expected_result') if 'expected_result' in kwargs else None
        start_time = datetime.now()
        result: int = func(*args, **kwargs)
        end_time = datetime.now()
        elapsed_time = end_time - start_time
        minutes, seconds = divmod(int(elapsed_time.total_seconds()), 60)
        print(f"Elapsed time: {minutes}:{seconds:02d}")

        if expected_result is None:
            print(f"New result: {result}")
        elif result != expected_result:
            raise AssertionError(f"Expected {expected_result}, but got {result}.")
        else:
            print(f"Result is as expected: {result}")
        return result

    return wrapper
