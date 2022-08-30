
import json
from typing import List

from billiards.dynamics import DynamicState
from billiards.geometry import PathParams

class Input:
    title: str
    description: str
    paths: List[PathParams]
    initialConditions: List[DynamicState]
    outputFile: str
    iterations: int

    def __init__(self, path):
        params = json.load(open(path))
        self.title = params["title"]
        self.description = params["description"]
        self.paths = list(map(PathParams, params["paths"]))
        self.initialConditions = list(map(DynamicState, params["initialConditions"]))
        self.outputFile = params["outputFile"]   
        self.iterations = params["iterations"] 