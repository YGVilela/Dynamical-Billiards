# Change that to use pathlib
import sys
from sympy import parse_expr
sys.path.append(".")

from billiards.input import Input
from billiards.graphics import GraphicsMatPlotLib
from billiards.geometry import SimplePath, ComposedPath

parameters = Input(sys.argv[1])
pathParams = parameters.paths
paths = []
for params in pathParams:
    paths.append(SimplePath(params.t0, params.t1, params.x, params.y))

composed = ComposedPath(paths)

initialConditions = parameters.initialConditions[0]
t = parse_expr(initialConditions.t)
theta = parse_expr(initialConditions.theta)
[x0, y0] = composed.get_point(t, evaluate=True)

graphics = GraphicsMatPlotLib(composed, t, theta)
graphics.render()
graphics.figure.savefig(parameters.outputFile)

