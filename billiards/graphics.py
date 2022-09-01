from typing import Any, List
from numpy import linspace, array, append
from math import ceil, pi
from matplotlib.pyplot import figure, show, savefig

from billiards.geometry import ComposedPath

class GraphicsMatPlotLib:
    boundary: ComposedPath
    # Figure out how to type these
    points: List[Any]
    states: List[Any]
    figure: Any
    ax: Any

    def __init__(self, boundary: ComposedPath, dynamicStates: List[Any] = [], renderPrecision=.1):
        self.boundary = boundary
        self.figure = figure()

        # Add table to figure
        lengths = linspace(0, self.boundary.lengthFloat, ceil(self.boundary.lengthFloat / renderPrecision))

        arrayX, arrayY = array(list(map(lambda s: self.boundary.get_point(s, evaluate=True), lengths))).T

        # Init points
        pointsX = []
        pointsY = []
        statesS = []
        statesTheta = []
        for state in dynamicStates:
            [x, y] = boundary.get_point(state.t, evaluate=True)
            pointsX.append(x)
            pointsY.append(y)
            statesS.append(state.t)
            statesTheta.append(state.theta)

        # Plot trajectories
        ax = self.figure.add_subplot(121)
        ax.axes.set_aspect('equal')
        ax.plot(arrayX, arrayY)
        self.points, = ax.plot(pointsX, pointsY)

        # Plot orbits
        ax = self.figure.add_subplot(122)
        ax.axes.set_aspect('equal')
        ax.set_xlim([float(boundary.t0.evalf()), float(boundary.t1.evalf())])
        ax.set_ylim([0, pi])
        self.states, = ax.plot(statesS, statesTheta, "o")

    def add_points(self, dynamicStates: List[Any]):
        pointsX = []
        pointsY = []
        statesS = []
        statesTheta = []
        for state in dynamicStates:
            [x, y] = self.boundary.get_point(state.t, evaluate=True)
            pointsX.append(x)
            pointsY.append(y)
            statesS.append(state.t)
            statesTheta.append(state.theta)

        self.points.set_xdata(append(self.points.get_xdata(), pointsX))
        self.points.set_ydata(append(self.points.get_ydata(), pointsY))
        self.states.set_xdata(append(self.states.get_xdata(), statesS))
        self.states.set_ydata(append(self.states.get_ydata(), statesTheta))

    def show(self):
        show()

    def save(self, path):
        savefig(path)

    def plot_ray_and_path(ray, path):
        t = linspace(0, path.lengthFloat, ceil(path.lengthFloat / 0.1))

        x, y = array(list(map(lambda s: path.get_point(s, evaluate=True), t))).T
        fig = figure()
        ax = fig.add_subplot(111)
        ax.axes.set_aspect('equal')

        ax.plot(x, y)
        ax.plot([float(ray.p1.x.evalf()), float((ray.p2.x).evalf())], [float(ray.p1.y.evalf()), float((ray.p2.y).evalf())])
        show()


# class GraphicsPyPlot:
#     def render(boundaries, x0, y0, deltaT = .01):
#         t = linspace(0, boundaries.lengthFloat, ceil(boundaries.lengthFloat / deltaT))

#         points = DataFrame(map(lambda s: boundaries.get_point(s, evaluate=True), t), columns=["x", "y"])

#         figure = px.line(points, x = "x", y = "y")
#         figure.update_yaxes(
#             scaleanchor = "x",
#             scaleratio = 1,
#         )
#         figure.add_scatter(x=[x0], y=[y0], showlegend=False, mode="lines")

#         return figure

    