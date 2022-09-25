import os
from pathlib import Path
import sys
from typing import List
from billiards.billiards import Billiard, iterate_parallel, iterate_serial
from billiards.geometry import ComposedPath, SimplePath
from billiards.graphics import GraphicsMatPlotLib
from billiards.input import Input, PathParams
from billiards.time import sharedTimer


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
    billiard = Billiard(
        boundary,
        initialConditions=parameters.initialConditions,
        method=parameters.method,
        orbitsFolder=parameters.orbitsFolder
    )

    # Execute dynamics
    if parameters.parallelize:
        idTimer = sharedTimer.start_operation("iterate_parallel")
        iterate_parallel(billiard, parameters.iterations, parameters.threads)
        sharedTimer.end_operation("iterate_parallel", idTimer)
    else:
        idTimer = sharedTimer.start_operation("iterate_serial")
        iterate_serial(billiard, parameters.iterations)
        sharedTimer.end_operation("iterate_serial", idTimer)

    # Save trajectories and orbit
    figure = None
    if parameters.show or parameters.saveImage:
        figure = GraphicsMatPlotLib(
            billiard.boundary, orbits=billiard.orbits
        ).plot()
    basePath = sys.argv[1].replace(".json", "")
    if parameters.saveImage or parameters.saveBilliard:
        Path(basePath).mkdir(exist_ok=True)

    if parameters.show:
        GraphicsMatPlotLib.show(figure)

    if parameters.saveImage:
        GraphicsMatPlotLib.save(figure, os.path.join(basePath, "plot.png"))

    if parameters.saveBilliard:
        billiard.save(basePath)

    print(sharedTimer.stats())
