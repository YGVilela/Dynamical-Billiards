from typing import List
from numpy import linspace, array, concatenate
from math import ceil, log, pi
from matplotlib.pyplot import figure as plt_figure, show as plt_show
from matplotlib import use as mpl_use
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from PySimpleGUI import Canvas

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
        plotNextDirection=False,
        fig=None
    ):
        if fig is None:
            fig = plt_figure()
        else:
            fig.clf(True)
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
                boundaryPoints.append([x, y])

                timer.end_operation("evaluate_boundary", idPlotBoundary)

        # Get (orbit) points
        phasePoints = [[], []]
        directions = []
        idPlotPath = timer.start_operation("evaluate_orbits")
        for orbit in self.orbits:
            if plotBoundary:
                boundaryPoints.append([orbit.points["x"], orbit.points["y"]])
            if plotPhase:
                phasePoints[0].append(orbit.points["t"])
                phasePoints[1].append(orbit.points["theta"])
            if plotNextDirection:
                point = boundary.get_point(
                    orbit.currentCondition[0], evaluate=True
                )
                directions.append(point)
        timer.end_operation("evaluate_orbits", idPlotPath)

        # Actually plot
        # Figure a better way to do this!
        idPlotOrbit = timer.start_operation("plot_objects")
        if plotBoundary and plotPhase:
            axBoundary = fig.add_subplot(121)
            axPhase = fig.add_subplot(122)
        else:
            axBoundary = axPhase = fig.add_subplot()

        if plotBoundary:
            axBoundary.set_aspect('equal')
            for x, y in boundaryPoints:
                axBoundary.plot(x, y)
            if plotNextDirection:
                for x, y in directions:
                    axBoundary.scatter([x], [y])

        if plotPhase:
            axPhase.set_aspect('equal')
            axPhase.set_xlim([
                float(boundary.t0.evalf()),
                float(boundary.t1.evalf())
            ])
            axPhase.set_ylim([0, pi])

            tArray = concatenate(phasePoints[0])
            thetaArray = concatenate(phasePoints[1])

            # This should be adjusted dynamically
            markerSize = 20 / max(log(len(tArray), 10), 1)

            axPhase.scatter(tArray, thetaArray, s=markerSize)

        timer.end_operation("plot_objects", idPlotOrbit)

        return fig

    def show(figure):
        plt_figure(figure.number)
        plt_show()

    def save(figure, path: str):
        figure.savefig(path)

    def render_on_canvas(figure, canvas: Canvas):
        figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
        figure_canvas_agg.draw()
        figure_canvas_agg.get_tk_widget().pack(
            side="top", fill="both", expand=1
        )
        return figure_canvas_agg
