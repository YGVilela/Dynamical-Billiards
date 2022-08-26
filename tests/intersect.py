from sympy import Ray2D, cos, sin, pi
import sys
sys.path.append(".")

from billiards.dynamics import firstIntersection
from billiards.geometry import SimplePath

ray = Ray2D((1, 0), (2, 0))
path = SimplePath("0", "2*pi", "cos(t)", "sin(t)")

nextT = firstIntersection(ray, path)
print(nextT)

newPoint = path.get_point(nextT, evaluate=True)
print(newPoint)
