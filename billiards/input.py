
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

    def __init__(self, path):
        params = json.load(open(path))
        # self.title = params["title"]
        # self.description = params["description"]
        self.paths = list(map(PathParams, params["paths"]))
        self.initialConditions = flat_array([parse_conditions(config) for config in params["initialConditions"]])
        self.iterations = params["iterations"] 

        if "method" in params:
            self.method = params["method"]
        else:
            self.method = "bissec"

def parse_conditions(dictionaire):
    count = 1
    if "instances" in dictionaire:
        count = dictionaire["instances"]

    return [parse_single_condition(dictionaire) for _ in range(count)]
    
def parse_single_condition(dictionaire):
    if not "t" in dictionaire:
        raise Exception("t is missing in dictionaire"+str(dictionaire))
    elif dictionaire["t"] == "Random":
        phiLow = to_number(dictionaire["tRange"][0])
        phiHigh = to_number(dictionaire["tRange"][1])
        phi0 = uniform(phiLow, phiHigh)
    else:
        phi0 = to_number(dictionaire["t"])


    if not "theta" in dictionaire:
        raise Exception("theta is missing in dictionaire"+str(dictionaire))
    elif dictionaire["theta"] == "Random":
        thetaLow = to_number(dictionaire["thetaRange"][0])
        thetaHigh = to_number(dictionaire["thetaRange"][1])
        theta0 = uniform(thetaLow, thetaHigh)
    else:
        theta0 = to_number(dictionaire["theta"])

    return (phi0, theta0)