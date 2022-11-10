from typing import Callable, List
import billiards.numeric_methods.methods as methods


METHODS = {
    "Bissection": methods.find_zero_bissec,
    "Newton": methods.find_zero_newton,
    "Regula Falsi": methods.find_zero_regula_falsi,
}

DEFAULT_METHOD = "Newton"


def find_zero(function: Callable[[float], List[float]], x_1: float,
              x_2: float, acc=1e-12, max_iter=100, method=DEFAULT_METHOD):

    if method not in METHODS:
        raise Exception(f"Invalid method {method}")

    handler = METHODS[method]
    return handler(function, x_1, x_2, acc, max_iter)
