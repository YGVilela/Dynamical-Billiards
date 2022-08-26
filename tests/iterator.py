import json

# Change that to use pathlib
import sys

sys.path.append(".")

from billiards.input import Input
from billiards.dynamics import iterate
# from billiards.graphics import plot_trajectory
from billiards.geometry import SimplePath, ComposedPath
from sympy import parse_expr

parameters = Input(sys.argv[1])
pathParams = parameters.paths
paths = []
for params in pathParams:
    paths.append(SimplePath(params.t0, params.t1, params.x, params.y))

composed = ComposedPath(paths)

initialConditions = parameters.initialConditions[0]
t = parse_expr(initialConditions.t)
theta = parse_expr(initialConditions.theta)

iterate(t, theta, composed)