from typing import List, Tuple
from billiards.dynamics import make_billiard_map
from billiards.geometry import ComposedPath
from pandas import DataFrame
from billiards.time import sharedTimer as timer
from progress.bar import Bar

class Orbit:
    initialCondition: Tuple[float]
    currentCondition: Tuple[float]
    points: DataFrame
    

    def __init__(self, initialCondition, evaluation):
        self.initialCondition = initialCondition
        self.currentCondition = initialCondition
        self.points = DataFrame([{
            "t": initialCondition[0],
            "theta": initialCondition[1],
            "x": evaluation[0],
            "y": evaluation[1]
        }])

    def add_evaluation(self, currentCondition, evaluation):
        newRow = [
            currentCondition[0],
            currentCondition[1],
            evaluation[0],
            evaluation[1]
        ]
        self.points.loc[len(self.points.index)] = newRow
        self.currentCondition = currentCondition

class Billiard:
    boundary: ComposedPath
    orbits: List[Orbit]

    def __init__(self, boundary: ComposedPath, initialConditions: List[Tuple[float]] = [], method = "newton"):
        self.boundary = boundary
        self.orbits = [Orbit((t[0], t[1]), boundary.get_point(t[0], evaluate=True)) for t in initialConditions]
        self.billiardMap = make_billiard_map(boundary, method=method)

    def iterate(self, indexes: List[int] = None, bar: Bar = None):
        if indexes == None:
            indexes = range(self.orbits.__len__())

        for index in indexes:
            condition = self.orbits[index].currentCondition

            idMap = timer.start_operation("map")
            nextCondition = self.billiardMap(condition[0], condition[1])
            timer.end_operation("map", idMap)

            idGetPoint = timer.start_operation("get_point")
            evaluation = self.boundary.get_point(nextCondition[0], evaluate=True)
            timer.end_operation("get_point", idGetPoint)

            self.orbits[index].add_evaluation(nextCondition, evaluation)
            if bar != None: bar.next()
        
            