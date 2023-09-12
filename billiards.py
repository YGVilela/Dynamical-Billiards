import json
import os
import sys
from pathlib import Path

from billiards.data_manager import DataManager
from billiards.graphics.mpl import GraphicsMatPlotLib
from billiards.core.geometry import ComposedPath
from billiards.numeric_methods import DEFAULT_METHOD
from billiards.utils.misc import flat_array, parse_conditions
from billiards.utils.iterator import iterate_parallel, iterate_serial
from billiards.utils.time import sharedTimer

dm = DataManager()


def load_simulation_variables(path: str):
    params = json.load(open(path))
    simulationVars = {}

    # Create/load billiard
    print("Loading billiard")
    simulationVars["name"] = params["name"]
    if not dm.simulation_exists(simulationVars["name"]):
        boundaryName = load_boundary_from_params(params["boundary"])

        dm.create_simulation(simulationVars["name"], boundaryName)

    simulationVars["billiard"] = dm.load_simulation_billiard(
        simulationVars["name"])

    # Add given initial conditions
    print("Adding initial conditions")
    if "initialConditions" in params:
        conditionArray = params["initialConditions"]
        initialConditions = flat_array([
            parse_conditions(config) for config in conditionArray
        ])

        simulationVars["billiard"].add_orbits(initialConditions)

    # Parse simulation configs
    print("Parsing simulation configs")
    simulationVars["iterations"] = int(params["iterations"])

    simulationVars["parallel"] = "parallel" in params and params["parallel"]

    if "threads" in params:
        simulationVars["threads"] = params["threads"]
    else:
        simulationVars["threads"] = 2

    if "method" in params:
        simulationVars["method"] = params["method"]
    else:
        simulationVars["method"] = DEFAULT_METHOD

    # Parse other variables
    simulationVars["show"] = "show" in params and params["show"]

    simulationVars["saveImagesAt"] = None
    if "saveImagesAt" in params:
        simulationVars["saveImagesAt"] = params["saveImagesAt"]

    return simulationVars


def load_boundary_from_params(boundaryParams):
    print("Loading boundary")
    boundaryName = boundaryParams["name"]
    if not dm.boundary_exists(boundaryName):
        boundary = ComposedPath.from_json(boundaryParams["paths"])

        dm.create_boundary(boundaryName, boundary)

    return boundaryName


if __name__ == "__main__":
    # Init objects from given argument
    simulationVars = load_simulation_variables(sys.argv[1])

    # Execute dynamics
    if simulationVars["parallel"]:
        print("Executing parallel")
        idTimer = sharedTimer.start_operation("iterate_parallel")
        iterate_parallel(
            simulationVars["billiard"],
            simulationVars["iterations"],
            simulationVars["threads"],
            method=simulationVars["method"]
        )
        sharedTimer.end_operation("iterate_parallel", idTimer)
    else:
        print("Executing serial")
        idTimer = sharedTimer.start_operation("iterate_serial")
        iterate_serial(
            simulationVars["billiard"],
            simulationVars["iterations"],
            method=simulationVars["method"]
        )
        sharedTimer.end_operation("iterate_serial", idTimer)

    # Update orbits
    print("Updating orbits")
    dm.upsert_simulation_orbits(
        simulationVars["name"],
        simulationVars["billiard"].orbits
    )

    # Save figures
    print("Saving figures")
    if simulationVars["saveImagesAt"] is not None:
        Path(simulationVars["saveImagesAt"]).mkdir(exist_ok=True, parents=True)

        trajectory = GraphicsMatPlotLib(
            simulationVars["billiard"].boundary,
            simulationVars["billiard"].orbits
        ).plot(plotBoundary=True, plotPhase=False)
        phase = GraphicsMatPlotLib(
            simulationVars["billiard"].boundary,
            simulationVars["billiard"].orbits
        ).plot(plotBoundary=False, plotPhase=True)

        trajectoryPath = os.path.join(
            simulationVars["saveImagesAt"], "trajectory.png"
        )
        GraphicsMatPlotLib.save(trajectory, trajectoryPath)

        phasePath = os.path.join(
            simulationVars["saveImagesAt"], "phase.png"
        )
        GraphicsMatPlotLib.save(phase, phasePath)

    # Show results
    print("Showing ")
    if simulationVars["show"]:
        GraphicsMatPlotLib.show()

    print(sharedTimer.stats())
