import sys
from typing import List
from billiards.billiards import Billiard
from billiards.geometry import ComposedPath, SimplePath
from billiards.graphics import GraphicsMatPlotLib
from billiards.input import Input, PathParams
from billiards.time import sharedTimer
from progress.bar import Bar

def getBoundary(pathParams: List[PathParams]):
    paths = []
    for params in pathParams:
        paths.append(SimplePath(params.t0, params.t1, params.x, params.y))

    composed = ComposedPath(paths)
    if not composed.is_closed():
        raise Exception("Can't simmulate on non-closed curves.")

    if not composed.is_continuous():
        raise Exception("Can't simmulate on discontinuous curves.")

    return composed

if __name__ == "__main__":
    # Init objects from given argument
    parameters = Input(sys.argv[1])
    pathParams = parameters.paths
    boundary = getBoundary(pathParams)
    billiard = Billiard(boundary, parameters.initialConditions, parameters.method)

    # Execute dynamics
    bar = Bar('Iterating', suffix='%(percent)d%% - %(eta)ds', max=parameters.iterations*len(billiard.orbits))
    for index in range(0, parameters.iterations):
        idIteration = sharedTimer.start_operation("iterate")
        billiard.iterate(bar = bar)
        sharedTimer.end_operation("iterate", idIteration)

    bar.finish()

    # Save trajectories and orbit
    fig = GraphicsMatPlotLib(billiard)
    fig.show()
    print(sharedTimer.stats())

