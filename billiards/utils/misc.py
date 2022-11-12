from numbers import Number
from random import uniform

from sympy import parse_expr


def flat_array(array):
    flatenedArray = []
    for sublist in array:
        for item in sublist:
            flatenedArray.append(item)

    return flatenedArray


def to_number(value):
    parsedValue = None
    if isinstance(value, Number):
        parsedValue = .0 + value
    elif isinstance(value, str):
        expression = parse_expr(value)
        parsedValue = float(expression.evalf())
    else:
        raise Exception(
            "value must be a mathematical expression (string) or a number." +
            "Received" + type(value)
        )

    return parsedValue


def to_expr(value):
    expression = None
    if isinstance(value, Number):
        expression = parse_expr("0.0") + value
    elif isinstance(value, str):
        expression = parse_expr(value)
    else:
        raise Exception(
            "value must be a mathematical expression (string) or a number." +
            "Received" + type(value)
        )
    return expression


def parse_conditions(dictionaire):
    count = 1
    if "instances" in dictionaire:
        count = dictionaire["instances"]

    return [parse_single_condition(dictionaire) for _ in range(count)]


def parse_single_condition(dictionaire):
    if "t" not in dictionaire:
        raise Exception("t is missing in dictionaire" + str(dictionaire))
    elif dictionaire["t"] == "Random":
        phiLow = to_number(dictionaire["tRange"][0])
        phiHigh = to_number(dictionaire["tRange"][1])
        phi0 = uniform(phiLow, phiHigh)
    else:
        phi0 = to_number(dictionaire["t"])

    if "theta" not in dictionaire:
        raise Exception("theta is missing in dictionaire" + str(dictionaire))
    elif dictionaire["theta"] == "Random":
        thetaLow = to_number(dictionaire["thetaRange"][0])
        thetaHigh = to_number(dictionaire["thetaRange"][1])
        theta0 = uniform(thetaLow, thetaHigh)
    else:
        theta0 = to_number(dictionaire["theta"])

    return (phi0, theta0)
