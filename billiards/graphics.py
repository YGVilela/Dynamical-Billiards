from numpy import linspace, array, concatenate
from math import ceil, pi
from matplotlib.pyplot import figure, show

from billiards.billiards import Billiard
from billiards.time import sharedTimer as timer


class GraphicsMatPlotLib:
    def __init__(self, billiards: Billiard, renderPrecision=.1):
        self.figure = figure()

        # Add table to figure
        idPlotBoundary = timer.start_operation("plot_boundary")
        numIntervals = ceil(billiards.boundary.lengthFloat / renderPrecision)
        tValues = linspace(0, billiards.boundary.lengthFloat, numIntervals)

        arrayX, arrayY = array([
            billiards.boundary.get_point(t, evaluate=True) for t in tValues
        ]).T

        ax = self.figure.add_subplot(121)
        ax.axes.set_aspect('equal')
        ax.plot(arrayX, arrayY)
        timer.end_operation("plot_boundary", idPlotBoundary)

        # Init points
        statesS = []
        statesTheta = []
        stateColor = []
        idPlotPath = timer.start_operation("plot_paths")
        for orbit in billiards.orbits:
            p, = ax.plot(orbit.points["x"], orbit.points["y"])
            statesS.append(orbit.points["t"])
            statesTheta.append(orbit.points["theta"])
            stateColor.append([p.get_color()] * len(orbit.points["t"]))
        timer.end_operation("plot_paths", idPlotPath)

        # Plot orbits
        idPlotOrbit = timer.start_operation("plot_orbit")
        ax = self.figure.add_subplot(122)
        ax.axes.set_aspect('equal')
        ax.set_xlim([
            float(billiards.boundary.t0.evalf()),
            float(billiards.boundary.t1.evalf())
        ])
        ax.set_ylim([0, pi])

        tArray = concatenate(statesS)
        thetaArray = concatenate(statesTheta)
        colorArray = concatenate(stateColor)

        # This should be adjusted dynamically
        markerSize = 1

        ax.scatter(tArray, thetaArray, s=markerSize, c=colorArray)
        timer.end_operation("plot_orbit", idPlotOrbit)

    def show(self):
        show()

    def save(self, path: str):
        self.figure.savefig(path)
