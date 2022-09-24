import json
from multiprocess import Pool
import os
from pathlib import Path
from typing import Callable, List, Tuple
from billiards.dynamics import make_billiard_map
from billiards.geometry import ComposedPath
from pandas import DataFrame, read_csv
from billiards.time import sharedTimer as timer


class Orbit:
    initialCondition: Tuple[float, float]
    currentCondition: Tuple[float, float]
    points: DataFrame
    billiardMap: Callable[
        [Tuple[float, float]],
        Tuple[Tuple[float, float], Tuple[float, float]]
    ]

    def __init__(
        self,
        billiardMap,
        pointsCsv: str = None,
        initialCondition: Tuple[float, float] = None,
        initialPoint: Tuple[float, float] = None
    ):

        self.billiardMap = billiardMap
        if pointsCsv is not None:
            dataFrame = read_csv(pointsCsv)
            self.initialCondition = (
                dataFrame.loc[0]["t"],
                dataFrame.loc[0]["theta"]
            )
            self.currentCondition = (
                dataFrame.loc[len(dataFrame.index) - 1]["t"],
                dataFrame.loc[len(dataFrame.index) - 1]["theta"]
            )
            self.points = dataFrame
        elif initialCondition is not None:
            self.initialCondition = initialCondition
            self.currentCondition = initialCondition
            self.points = DataFrame([{
                "t": initialCondition[0],
                "theta": initialCondition[1],
                "x": initialPoint[0],
                "y": initialPoint[1]
            }])
        else:
            raise Exception(
                "Csv with dataframe or initial" +
                "conditions needed to create the orbit."
            )

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
        t, theta = self.initialCondition
        fileName = str(t) + "_" + str(theta) + ".csv"
        path = os.path.join(folder, fileName)
        self.points.to_csv(path, index=False)


class Billiard:
    orbits: List[Orbit]
    boundary: ComposedPath

    def __init__(
        self,
        boundary: ComposedPath,
        initialConditions:
        List[Tuple[float, float]] = [],
        method="newton",
        orbitsFolder: str = None
    ):

        billiardMap = make_billiard_map(boundary, method=method)
        self.billiardMap = billiardMap
        self.orbits = [
            Orbit(
                billiardMap,
                initialCondition=t,
                initialPoint=boundary.get_point(t[0], evaluate=True)
            ) for t in initialConditions
        ]
        self.boundary = boundary
        if orbitsFolder is not None:
            for fileName in os.listdir(orbitsFolder):
                if fileName.endswith(".csv"):
                    self.orbits.append(
                        Orbit(
                            billiardMap,
                            pointsCsv=os.path.join(orbitsFolder, fileName)
                        )
                    )

    def iterate(
        self,
        indexes: List[int] = None,
        callback=None,
        iterations=1
    ):
        if indexes is None:
            indexes = range(self.orbits.__len__())

        for index in indexes:
            for _ in range(iterations):
                idMap = timer.start_operation("iterate_orbit")
                self.orbits[index].iterate()
                timer.end_operation("iterate_orbit", idMap)

                if callback is not None:
                    callback()

    def iterate_parallel(
        self,
        callback=None,
        iterations=10,
        poolSize=2
    ):

        def iterateOrbit(orbit: Orbit):
            for _ in range(iterations):
                idMap = timer.start_operation("iterate_orbit")
                orbit.iterate()
                timer.end_operation("iterate_orbit", idMap)

                if callback is not None:
                    callback()

            return orbit

        pool = Pool(poolSize)

        res = pool.map(iterateOrbit, self.orbits)

        for index in range(len(res)):
            self.orbits[index] = res[index]

    def save(self, folder: str):
        # Saving boundary
        Path(folder).mkdir(exist_ok=True)
        boundaryJson = self.boundary.to_json()
        path = os.path.join(folder, "boundary.json")
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(boundaryJson, f, ensure_ascii=False, indent=4)

        # Saving orbits
        orbitsFolder = os.path.join(folder, "orbits")
        Path(orbitsFolder).mkdir(exist_ok=True)
        for orbit in self.orbits:
            orbit.save_points(orbitsFolder)

    def load(folder: str):
        path = os.path.join(folder, "boundary.json")
        dictionary = json.load(open(path))
        boundary = ComposedPath.from_json(dictionary)

        orbitsFolder = os.path.join(folder, "orbits")
        return Billiard(boundary, orbitsFolder=orbitsFolder)

    def add_orbit(self, initialCondition: Tuple[float, float]):
        newOrbit = Orbit(
            self.billiardMap,
            initialCondition=initialCondition,
            initialPoint=self.boundary.get_point(
                initialCondition[0], evaluate=True
            )
        )
        self.orbits.append(newOrbit)

    def remove_orbit(self, index):
        return self.orbits.pop(index)
