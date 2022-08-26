
import json
from typing import List


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

class InitialConditions:
    t: str
    theta: str

    def __init__(self, dictionaire):
        self.t = dictionaire["t"]
        self.theta = dictionaire["theta"]

class Input:
    title: str
    description: str
    paths: List[PathParams]
    initialConditions: List[InitialConditions]
    outputFile: str

    def __init__(self, path):
        params = json.load(open(path))
        self.title = params["title"]
        self.description = params["description"]
        self.paths = list(map(PathParams, params["paths"]))
        self.initialConditions = list(map(InitialConditions, params["initialConditions"]))
        self.outputFile = params["outputFile"]    