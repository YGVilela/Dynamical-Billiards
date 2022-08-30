import sys
from typing import List
from billiards.dynamics import iterate
from billiards.geometry import ComposedPath, SimplePath
from billiards.graphics import GraphicsMatPlotLib
from billiards.input import Input, PathParams

def getBoundary(pathParams: List[PathParams]):
    paths = []
    for params in pathParams:
        paths.append(SimplePath(params.t0, params.t1, params.x, params.y))

    composed = ComposedPath(paths)

    return composed

if __name__ == "__main__":
    # Init objects from given argument
    parameters = Input(sys.argv[1])
    pathParams = parameters.paths
    boundary = getBoundary(pathParams)
    dynamicState = parameters.initialConditions[0]

    # Execute dynamics
    points = [dynamicState]
    for index in range(0, parameters.iterations):
        print(dynamicState, type(dynamicState.t))
        nextState = iterate(dynamicState, boundary)
        points.append(nextState)
        dynamicState = nextState

    # Save trajectories and orbit
    graphics = GraphicsMatPlotLib(boundary, points)
    graphics.show()

