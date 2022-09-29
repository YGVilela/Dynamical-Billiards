from typing import List
from numpy import linspace, array, concatenate
from math import ceil, log, pi
from matplotlib.pyplot import figure as plt_figure, show as plt_show
from matplotlib import use as mpl_use

from billiards.billiards import Orbit
from billiards.geometry import ComposedPath
from billiards.time import sharedTimer as timer

mpl_use("TkAgg")


class GraphicsMatPlotLib:
    def __init__(
        self,
        boundary: ComposedPath,
        orbits: List[Orbit] = [],
        renderPrecision=.1
    ):
        self.boundary = boundary
        self.orbits = orbits
        self.renderPrecision = renderPrecision

    def plot(
        self,
        plotBoundary=True,
        plotPhase=True,
        fig=None,
        markerSize=None,
        orbitIndexes: List[int] = None
    ):
        if fig is None:
            fig = plt_figure()
        else:
            fig.clf(True)

        if orbitIndexes is None:
            orbitIndexes = range(len(self.orbits))

        boundary = self.boundary

        # Get boundary
        boundaryPoints = []
        if plotBoundary:
            numIntervals = ceil(
                boundary.lengthFloat / self.renderPrecision
            )
            if numIntervals != 0:
                idPlotBoundary = timer.start_operation("evaluate_boundary")

                tValues = linspace(
                    0, boundary.lengthFloat, numIntervals
                )

                x, y = array([
                    boundary.get_point(t, evaluate=True) for t in tValues
                ]).T
                boundaryPoints = [x, y]

                timer.end_operation("evaluate_boundary", idPlotBoundary)

        # Get (orbit) points
        phasePoints = [[], []]
        trajectoryPoints = []
        # directions = []
        idPlotPath = timer.start_operation("evaluate_orbits")
        for index in orbitIndexes:
            orbit = self.orbits[index]
            if plotBoundary:
                trajectoryPoints.append([orbit.points["x"], orbit.points["y"]])
            if plotPhase:
                phasePoints[0].append(orbit.points["t"])
                phasePoints[1].append(orbit.points["theta"])

        timer.end_operation("evaluate_orbits", idPlotPath)

        # Actually plot
        # Figure a better way to do this!
        idPlotOrbit = timer.start_operation("plot_objects")
        if plotBoundary and plotPhase:
            axBoundary = fig.add_subplot(121)
            axPhase = fig.add_subplot(122)
        else:
            axBoundary = axPhase = fig.add_subplot()

        # colors = []
        if plotBoundary:
            axBoundary.set_aspect('equal')
            if len(boundaryPoints) > 0:
                axBoundary.plot(boundaryPoints[0], boundaryPoints[1])
            for x, y in trajectoryPoints:
                p, = axBoundary.plot(x, y)
                # colors.append([p.get_color()] * len(x))

        if plotPhase:
            axPhase.set_aspect('equal')
            axPhase.set_xlim([
                float(boundary.t0.evalf()),
                float(boundary.t1.evalf())
            ])
            axPhase.set_ylim([0, pi])

            if len(phasePoints[0]) > 0:
                tArray = concatenate(phasePoints[0])
                thetaArray = concatenate(phasePoints[1])
                colorArray = None
                # if len(colors) > 0:
                #     colorArray = concatenate(colors)

                # This should be adjusted dynamically
                if markerSize is None:
                    markerSize = 20 / max(10 * log(len(tArray), 10), 1)

                axPhase.scatter(tArray, thetaArray, s=markerSize, c=colorArray)

        timer.end_operation("plot_objects", idPlotOrbit)

        return fig

    def show(figure):
        plt_figure(figure.number)
        plt_show()

    def save(figure, path: str):
        figure.savefig(path)
