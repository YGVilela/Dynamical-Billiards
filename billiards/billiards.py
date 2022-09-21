from typing import Callable, List, Tuple
from billiards.dynamics import make_billiard_map
from billiards.geometry import ComposedPath
from pandas import DataFrame
from billiards.time import sharedTimer as timer
from progress.bar import Bar

class Orbit:
    initialCondition: Tuple[float, float]
    currentCondition: Tuple[float, float]
    points: DataFrame
    billiardMap: Callable[[Tuple[float, float]], Tuple[Tuple[float, float], Tuple[float, float]]]
    

    def __init__(self, initialCondition, initialPoint, billiardMap):
        self.initialCondition = initialCondition
        self.currentCondition = initialCondition
        self.billiardMap = billiardMap
        self.points = DataFrame([{
            "t": initialCondition[0],
            "theta": initialCondition[1],
            "x": initialPoint[0],
            "y": initialPoint[1]
        }])

    def iterate(self):
        nextCondition, nextPoint = self.billiardMap(self.currentCondition)
        newRow = [
            nextCondition[0],
            nextCondition[1],
            nextPoint[0],
            nextPoint[1]
        ]
        self.points.loc[len(self.points.index)] = newRow
        self.currentCondition = nextCondition

class Billiard:
    orbits: List[Orbit]
    boundary: ComposedPath

    def __init__(self, boundary: ComposedPath, initialConditions: List[Tuple[float]] = [], method = "newton"):
        billiardMap = make_billiard_map(boundary, method=method)
        self.orbits = [Orbit((t[0], t[1]), boundary.get_point(t[0], evaluate=True), billiardMap) for t in initialConditions]
        self.boundary = boundary

    def iterate(self, indexes: List[int] = None, bar: Bar = None):
        if indexes == None:
            indexes = range(self.orbits.__len__())

        for index in indexes:
            idMap = timer.start_operation("iterate_orbit")
            self.orbits[index].iterate()
            timer.end_operation("iterate_orbit", idMap)

            if bar != None: bar.next()
        
            