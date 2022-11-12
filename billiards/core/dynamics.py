from math import acos, asin, cos, pi, sin
from typing import Callable, List, Optional, Tuple

from multiprocess import Pool
from pandas import DataFrame

from billiards.core.geometry import ComposedPath
from billiards.numeric_methods import find_zero
from billiards.utils.time import sharedTimer as timer


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
        id = timer.start_operation("iterateOrbit")
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
        timer.end_operation("iterateOrbit", id)


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


def get_objective_function(boundary: ComposedPath, phi0: float, theta0: float):
    ''' Receives the billiard boundary and returns the real function
    whose root is the argument of the next point in the billiard orbit.
    '''

    x0, y0 = boundary.get_point(phi0, evaluate=True)
    tangent_x0, tangent_y0 = boundary.get_tangent(phi0, evaluate=True)

    def func(phi: float):
        x, y = boundary.get_point(phi, evaluate=True)
        tangent_x, tangent_y = boundary.get_tangent(phi, evaluate=True)

        r_x = x - x0
        r_y = y - y0
        # (v_x, v_y) is perpendicular to the ray
        # (x0, y0) com inclinação theta0 com a tangente
        v_x = -(tangent_x0) * sin(theta0) - (tangent_y0) * cos(theta0)
        v_y = -(tangent_y0) * sin(theta0) + (tangent_x0) * cos(theta0)
        drx = tangent_x
        dry = tangent_y

        return r_x * v_x + r_y * v_y, drx * v_x + dry * v_y

    return func


def make_billiard_map(
    boundary: ComposedPath,
    factor=100,
    **kwargs
):
    '''Creates the billiard map for the given boundary.

    factor: To be documented

    **kwargs: arguments for the numeric method. To be documented.
    '''

    if "acc" not in kwargs:
        acc = 0.0000000000001
    else:
        acc = kwargs["acc"]
    if "max_iteracao" not in kwargs:
        max_iteracao = 100
    else:
        max_iteracao = kwargs["max_iteracao"]

    if boundary.periodic:
        periodo = boundary.lengthFloat
    else:
        raise Exception("Can't simulate on non-periodic boundary")

    def billiard_map(condition: Tuple[float, float], method: str = None):
        phi0, theta0 = condition
        func = get_objective_function(boundary, phi0, theta0)

        x_phi1 = y_phi1 = None
        if ((-acc < theta0) and (theta0 < acc)):
            theta1 = 0.0
            phi1 = phi0
            x_phi1, y_phi1 = boundary.get_point(phi1, evaluate=True)
        if ((pi - acc < theta0) and (theta0 < pi + acc)):
            theta1 = pi
            phi1 = phi0
            x_phi1, y_phi1 = boundary.get_point(phi1, evaluate=True)
        else:
            phi1 = find_zero(
                func,
                phi0 + factor * acc,
                phi0 + periodo - factor * acc,
                acc=acc,
                max_iter=max_iteracao,
                method=method)

            phi1 = phi1 % periodo

            x_phi1, y_phi1 = boundary.get_point(phi1, evaluate=True)
            x_phi0, y_phi0 = boundary.get_point(phi0, evaluate=True)
            dx_phi1, dy_phi1 = boundary.get_tangent(phi1, evaluate=True)

            r_x = x_phi1 - x_phi0
            r_y = y_phi1 - y_phi0
            t_x = dx_phi1
            t_y = dy_phi1
            norma = \
                pow(r_x * r_x + r_y * r_y, .5) * pow(t_x * t_x + t_y * t_y, .5)

            if ((r_x * t_x + r_y * t_y) / norma) > 1 / 2:
                theta1 = asin((r_x * t_y - r_y * t_x) / norma)
            elif ((r_x * t_x + r_y * t_y) / norma) < -1 / 2:
                theta1 = pi - asin((r_x * t_y - r_y * t_x) / norma)
            else:
                theta1 = acos((r_x * t_x + r_y * t_y) / norma)
        return ((phi1, theta1), (x_phi1, y_phi1))

    return billiard_map
