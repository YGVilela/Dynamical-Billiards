
import json
from random import uniform
from billiards.billiards import Billiard
from billiards.geometry import ComposedPath
from billiards.numeric_methods.index import DEFAULT_METHOD

from billiards.utils import flat_array, to_number
from billiards.data_manager import DataManager

dm = DataManager()


class PathParams:
    x: str
    y: str
    t0: str
    t1: str

    def __init__(self, dictionaire):
        self.x = dictionaire["x"]
        self.y = dictionaire["y"]
        self.t0 = dictionaire["t0"]
        self.t1 = dictionaire["t1"]


class SimulationConfig:
    name: str
    billiard: Billiard
    iterations: int
    parallel: bool
    threads: int
    method: str
    show: bool
    saveImagesAt: str

    def __init__(self, path: str):
        params = json.load(open(path))

        # Create/load billiard
        self.name = params["name"]
        if not dm.simulation_exists(self.name):
            boundaryName = load_boundary_from_params(params["boundary"])

            dm.create_simulation(self.name, boundaryName)

        self.billiard = dm.load_simulation_billiard(self.name)

        # Add given initial conditions
        if "initialConditions" in params:
            conditionArray = params["initialConditions"]
            initialConditions = flat_array([
                parse_conditions(config) for config in conditionArray
            ])

            self.billiard.add_orbits(initialConditions)

        # Parse simulation configs
        self.iterations = int(params["iterations"])

        self.parallel = "parallel" in params and params["parallel"]

        if "threads" in params:
            self.threads = params["threads"]
        else:
            self.threads = 2

        if "method" in params:
            self.method = params["method"]
        else:
            self.method = DEFAULT_METHOD

        # Parse other variables
        self.show = "show" in params and params["show"]

        self.saveImagesAt = None
        if "saveImagesAt" in params:
            self.saveImagesAt = params["saveImagesAt"]


def load_boundary_from_params(boundaryParams):
    boundaryName = boundaryParams["name"]
    if not dm.boundary_exists(boundaryName):
        boundary = ComposedPath.from_json(boundaryParams["paths"])

        dm.create_boundary(boundaryName, boundary)

    return boundaryName


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
