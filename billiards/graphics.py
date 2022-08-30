from typing import Any, List
from numpy import linspace, array, append
from math import ceil
from matplotlib.pyplot import figure, show

from billiards.geometry import ComposedPath

class GraphicsMatPlotLib:
    boundary: ComposedPath
    # Figure out how to type these
    points: List[Any]
    figure: Any
    ax: Any

    def __init__(self, boundary: ComposedPath, dynamicStates: List[Any] = [], renderPrecision=.1):
        self.boundary = boundary
        self.figure = figure()

        # Add table to figure
        lengths = linspace(0, self.boundary.lengthFloat, ceil(self.boundary.lengthFloat / renderPrecision))

        x, y = array(list(map(lambda s: self.boundary.get_point(s, evaluate=True), lengths))).T
        self.ax = self.figure.add_subplot(111)
        self.ax.axes.set_aspect('equal')
        self.ax.plot(x, y)

        # Init points
        pointsX = []
        pointsY = []
        for state in dynamicStates:
            [x, y] = boundary.get_point(state.t, evaluate=True)
            pointsX.append(x)
            pointsY.append(y)

        self.points, = self.ax.plot(pointsX, pointsY)

    def add_points(self, dynamicStates: List[Any]):
        pointsX = []
        pointsY = []
        for state in dynamicStates:
            [x, y] = self.boundary.get_point(state.t, evaluate=True)
            pointsX.append(x)
            pointsY.append(y)

        self.points.set_xdata(append(self.points.get_xdata(), x))
        self.points.set_ydata(append(self.points.get_ydata(), y))

    def show(self):
        show()

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

    