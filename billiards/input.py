
import json
from random import uniform
from typing import List, Tuple

from billiards.geometry import PathParams

from billiards.utils import flat_array, to_number


class Input:
    # title: str
    # description: str
    paths: List[PathParams]
    initialConditions: List[Tuple[float]]
    iterations: int
    method: str
    show: bool
    saveImage: bool
    saveBilliard: str
    orbitsFolder: str

    def __init__(self, path):
        params = json.load(open(path))
        # self.title = params["title"]
        # self.description = params["description"]
        self.paths = list(map(PathParams, params["paths"]))
        if "initialConditions" in params:
            conditionArray = params["initialConditions"]
            self.initialConditions = flat_array([
                parse_conditions(config) for config in conditionArray
            ])
        else:
            self.initialConditions = []

        self.iterations = params["iterations"]

        if "method" in params:
            self.method = params["method"]
        else:
            self.method = "newton"

        self.show = "show" in params and params["show"]
        self.saveImage = "saveImage" in params and params["saveImage"]
        self.saveBilliard = "saveBilliard" in params and params["saveBilliard"]

        if "orbitsFolder" in params:
            self.orbitsFolder = params["orbitsFolder"]
        else:
            self.orbitsFolder = None


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
