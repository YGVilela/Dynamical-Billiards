# A Python3 program to find if 2 given line segments intersect or not
# Accessed in
# https://www.geeksforgeeks.org/check-if-two-given-line-segments-intersect/
# on 2022/08/24
# This code is contributed by Ansh Riyal

from math import isclose
from numbers import Number
from sympy import Max, Min, parse_expr

# Given three collinear points p, q, r, the function checks if
# point q lies on line segment 'pr'


def onSegment(p, q, r):
    if ((q.x <= Max(p.x, r.x)) and (q.x >= Min(p.x, r.x)) and
            (q.y <= Max(p.y, r.y)) and (q.y >= Min(p.y, r.y))):
        return True
    return False


def orientation(p, q, r):
    # to find the orientation of an ordered triplet (p,q,r)
    # function returns the following values:
    # 0 : Collinear points
    # 1 : Clockwise points
    # 2 : Counterclockwise

    # See https://www.geeksforgeeks.org/orientation-3-ordered-points/amp/
    # for details of below formula.

    expr = ((q.y - p.y) * (r.x - q.x)) - ((q.x - p.x) * (r.y - q.y))
    val = float(expr.evalf())

    if isclose(val, 0):

        # Collinear orientation
        return 0
    elif (val > 0):

        # Clockwise orientation
        return 1
    elif (val < 0):

        # Counterclockwise orientation
        return 2

# The main function that returns true if
# the line segment 'p1q1' and 'p2q2' intersect.


def doIntersect(p1, q1, p2, q2):

    # Find the 4 orientations required for
    # the general and special cases
    o1 = orientation(p1, q1, p2)
    o2 = orientation(p1, q1, q2)
    o3 = orientation(p2, q2, p1)
    o4 = orientation(p2, q2, q1)

    # General case
    if ((o1 != o2) and (o3 != o4)):
        return True

    # Special Cases

    # p1 , q1 and p2 are collinear and p2 lies on segment p1q1
    if ((o1 == 0) and onSegment(p1, p2, q1)):
        return True

    # p1 , q1 and q2 are collinear and q2 lies on segment p1q1
    if ((o2 == 0) and onSegment(p1, q2, q1)):
        return True

    # p2 , q2 and p1 are collinear and p1 lies on segment p2q2
    if ((o3 == 0) and onSegment(p2, p1, q2)):
        return True

    # p2 , q2 and q1 are collinear and q1 lies on segment p2q2
    if ((o4 == 0) and onSegment(p2, q1, q2)):
        return True

    # If none of the cases
    return False


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