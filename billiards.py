import os
from pathlib import Path
import sys
from typing import List
from billiards.billiards import iterate_parallel, iterate_serial
from billiards.geometry import ComposedPath, SimplePath
from billiards.graphics import GraphicsMatPlotLib
from billiards.input import PathParams, SimulationConfig
from billiards.time import sharedTimer
from billiards.data_manager import DataManager

dm = DataManager()


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
    simulationConfig = SimulationConfig(sys.argv[1])

    # Execute dynamics
    if simulationConfig.parallel:
        idTimer = sharedTimer.start_operation("iterate_parallel")
        iterate_parallel(
            simulationConfig.billiard,
            simulationConfig.iterations,
            simulationConfig.threads,
            method=simulationConfig.method
        )
        sharedTimer.end_operation("iterate_parallel", idTimer)
    else:
        idTimer = sharedTimer.start_operation("iterate_serial")
        iterate_serial(
            simulationConfig.billiard,
            simulationConfig.iterations,
            method=simulationConfig.method
        )
        sharedTimer.end_operation("iterate_serial", idTimer)

    # Update orbits
    dm.upsert_simulation_orbits(
        simulationConfig.name,
        simulationConfig.billiard.orbits
    )

    # Save figures
    if simulationConfig.saveImagesAt is not None:
        Path(simulationConfig).mkdir(exist_ok=True)

        trajectory = GraphicsMatPlotLib(
            simulationConfig.billiard.boundary,
            simulationConfig.billiard.orbits
        ).plot(plotBoundary=True, plotPhase=False)
        phase = GraphicsMatPlotLib(
            simulationConfig.billiard.boundary,
            simulationConfig.billiard.orbits
        ).plot(plotBoundary=False, plotPhase=True)

        trajectoryPath = os.path.join(
            simulationConfig.saveImagesAt, "trajectory.png"
        )
        GraphicsMatPlotLib.save(trajectory, trajectoryPath)

        phasePath = os.path.join(
            simulationConfig.saveImagesAt, "phase.png"
        )
        GraphicsMatPlotLib.save(phase, phasePath)

    # Show results
    if simulationConfig.show:
        figure = GraphicsMatPlotLib(
            simulationConfig.billiard.boundary,
            simulationConfig.billiard.orbits
        ).plot()

        if simulationConfig.show:
            GraphicsMatPlotLib.show(figure)

    print(sharedTimer.stats())
