import json
import os
from pathlib import Path
from typing import Callable, List, Tuple
from billiards.dynamics import make_billiard_map
from billiards.geometry import ComposedPath
from pandas import DataFrame, read_csv
from billiards.time import sharedTimer as timer
from progress.bar import Bar

class Orbit:
    initialCondition: Tuple[float, float]
    currentCondition: Tuple[float, float]
    points: DataFrame
    billiardMap: Callable[[Tuple[float, float]], Tuple[Tuple[float, float], Tuple[float, float]]]
    

    def __init__(
            self,
            billiardMap, 
            pointsCsv:str=None,
            initialCondition: Tuple[float, float] = None,
            initialPoint: Tuple[float, float] = None
        ):

        self.billiardMap = billiardMap
        if pointsCsv != None:
            dataFrame = read_csv(pointsCsv)
            self.initialCondition = (dataFrame.loc[0]["t"], dataFrame.loc[0]["theta"])
            self.currentCondition = (dataFrame.loc[len(dataFrame.index)-1]["t"], dataFrame.loc[len(dataFrame.index)-1]["theta"])
            self.points = dataFrame
        elif initialCondition != None:
            self.initialCondition = initialCondition
            self.currentCondition = initialCondition
            self.points = DataFrame([{
                "t": initialCondition[0],
                "theta": initialCondition[1],
                "x": initialPoint[0],
                "y": initialPoint[1]
            }])
        else:
            raise Exception("Csv with dataframe or initial conditions needed to create the orbit.")

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

    def save_points(self, folder: str):
        fileName = str(self.initialCondition[0])+"_"+str(self.initialCondition[1])+".csv"
        path = os.path.join(folder, fileName)
        self.points.to_csv(path, index=False)


class Billiard:
    orbits: List[Orbit]
    boundary: ComposedPath

    def __init__(self, boundary: ComposedPath, initialConditions: List[Tuple[float, float]] = [], method = "newton", orbitsFolder: str = None):
        billiardMap = make_billiard_map(boundary, method=method)
        self.orbits = [
            Orbit(
                billiardMap,
                initialCondition=t,
                initialPoint=boundary.get_point(t[0], evaluate=True)
            ) for t in initialConditions
        ]
        self.boundary = boundary
        if orbitsFolder != None:
            for fileName in os.listdir(orbitsFolder):
                if fileName.endswith(".csv"):
                    self.orbits.append(
                        Orbit(billiardMap, pointsCsv=os.path.join(orbitsFolder, fileName))
                    )

    def iterate(self, indexes: List[int] = None, bar: Bar = None):
        if indexes == None:
            indexes = range(self.orbits.__len__())

        for index in indexes:
            idMap = timer.start_operation("iterate_orbit")
            self.orbits[index].iterate()
            timer.end_operation("iterate_orbit", idMap)

            if bar != None: bar.next()

    def save(self, folder: str):
        boundaryJson = self.boundary.to_json()
        path = os.path.join(folder, "boundary.json")
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(boundaryJson, f, ensure_ascii=False, indent=4)

        orbitsFolder = os.path.join(folder, "orbits")
        Path(orbitsFolder).mkdir(exist_ok=True)
        for orbit in self.orbits:
            orbit.save_points(orbitsFolder)
            
            