from multiprocess import Pool, Process, Manager
from typing import Callable, List, Optional, Tuple
from billiards.dynamics import make_billiard_map
from billiards.geometry import ComposedPath
from pandas import DataFrame
from billiards.time import sharedTimer as timer
from PySimpleGUI import Window, ProgressBar
from progress.bar import Bar


class Orbit:
    initialCondition: Tuple[float, float]
    currentCondition: Tuple[float, float]
    points: DataFrame
    billiardMap: Callable[
        [Tuple[float, float], Optional[str]],
        Tuple[Tuple[float, float], Tuple[float, float]]
    ]

    def __init__(
        self,
        boundary: ComposedPath,
        points: DataFrame = None,
        initialCondition: Tuple[float, float] = None
    ):

        self.billiardMap = make_billiard_map(boundary)
        if points is not None:
            # Todo: Check if points have the right format
            self.initialCondition = (
                points.loc[0]["t"],
                points.loc[0]["theta"]
            )
            self.currentCondition = (
                points.loc[len(points.index) - 1]["t"],
                points.loc[len(points.index) - 1]["theta"]
            )
            self.points = points
        elif initialCondition is not None:
            self.initialCondition = initialCondition
            self.currentCondition = initialCondition
            initialPoint = boundary.get_point(
                initialCondition[0], evaluate=True
            )
            self.points = DataFrame([{
                "t": initialCondition[0],
                "theta": initialCondition[1],
                "x": initialPoint[0],
                "y": initialPoint[1]
            }])
        else:
            raise Exception(
                "Dataframe with iterates or initial condition" +
                "needed to create the orbit."
            )

    def iterate(self, method=None):
        nextCondition, nextPoint = self.billiardMap(
            self.currentCondition, method=method
        )
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

    def __init__(
        self,
        boundary: ComposedPath,
        initialConditions: List[Tuple[float, float]] = [],
        orbits: List[Orbit] = None
    ):

        self.boundary = boundary
        if orbits is not None:
            self.orbits = orbits
        else:
            self.orbits = []

        for condition in initialConditions:
            t = condition[0]
            self.orbits.append(Orbit(
                boundary,
                initialCondition=condition,
                initialPoint=boundary.get_point(t, evaluate=True)
            ))

    def iterate(
        self,
        indexes: List[int] = None,
        callback=None,
        iterations=1,
        method: str = None
    ):
        if indexes is None:
            indexes = range(self.orbits.__len__())

        for index in indexes:
            for _ in range(iterations):
                idMap = timer.start_operation("iterate_orbit")
                self.orbits[index].iterate(method=method)
                timer.end_operation("iterate_orbit", idMap)

                if callback is not None:
                    callback()

    def iterate_parallel(
        self,
        callback=None,
        iterations=10,
        poolSize=2,
        method: str = None
    ):

        def iterateOrbit(orbit: Orbit):
            for _ in range(iterations):
                idMap = timer.start_operation("iterate_orbit")
                orbit.iterate(method=method)
                timer.end_operation("iterate_orbit", idMap)

                if callback is not None:
                    callback()

            return orbit

        pool = Pool(poolSize)

        res = pool.map(iterateOrbit, self.orbits)

        for index in range(len(res)):
            self.orbits[index] = res[index]

    def add_orbit(self, initialCondition: Tuple[float, float]):
        newOrbit = Orbit(
            self.boundary,
            initialCondition=initialCondition
        )
        self.orbits.append(newOrbit)

    # Todo: Consider keeping only this one
    def add_orbits(self, initialCondition: List[Tuple[float, float]]):
        for ic in initialCondition:
            newOrbit = Orbit(
                self.boundary,
                initialCondition=ic
            )
            self.orbits.append(newOrbit)

    def remove_orbit(self, index):
        return self.orbits.pop(index)


def iterate_serial(
    billiard: Billiard,
    iterations: int,
    GUI: bool = False,
    method: str = None
):
    totalIter = iterations * len(billiard.orbits)
    if GUI:
        window = Window(
            "Iterating...",
            layout=[[ProgressBar(totalIter, size=(50, 10), key="progress")]],
            finalize=True
        )
    else:
        bar = Bar(
            'Iterating', suffix='%(percent)d%% - %(eta)ds',
            max=totalIter
        )

    currentProgress = [0]

    def cb():
        if GUI:
            currentProgress[0] += 1
            window["progress"].update(currentProgress[0])
        else:
            bar.next()

    billiard.iterate(
        iterations=iterations,
        callback=cb,
        method=method
    )

    if GUI:
        window.close()
    else:
        bar.finish()


def iterate_parallel(
    billiard: Billiard,
    iterations: int,
    threads: int,
    GUI: bool = False,
    method: str = None
):
    manager = Manager()
    queue = manager.Queue()

    def cb():
        queue.put(1)

    def tick(queue, totalIter):
        currentProgress = 0
        if GUI:
            window = Window(
                "Iterating...",
                layout=[
                    [ProgressBar(totalIter, size=(50, 10), key="progress")]
                ],
                finalize=True
            )
        else:
            bar = Bar(
                'Iterating', suffix='%(percent)d%% - %(eta)ds',
                max=totalIter
            )

        while True:
            queue.get()
            currentProgress += 1
            if GUI:
                window["progress"].update(currentProgress)
            else:
                bar.next()

            if totalIter <= currentProgress:
                break

        if GUI:
            window.close()
        else:
            bar.finish()

    totalIter = iterations * len(billiard.orbits)
    consumer = Process(
        target=tick, args=[queue, totalIter]
    )
    consumer.start()

    billiard.iterate_parallel(
        iterations=iterations,
        callback=cb,
        poolSize=threads,
        method=method
    )

    consumer.join()
