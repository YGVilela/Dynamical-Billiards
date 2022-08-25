from numpy import linspace, array#, append
from math import ceil
from matplotlib.pyplot import figure

# from billiards.dynamics import iterate

class GraphicsMatPlotLib:
    def __init__(self, boundary, t0, theta0):
        self.boundary = boundary
        self.t = t0
        self.theta = theta0
        [self.currentX, self.currentY] = boundary.get_point(t0, evaluate=True)
        self.points = None
        self.figure = figure()

    def render(self, deltaT=0.1):
        t = linspace(0, self.boundary.lengthFloat, ceil(self.boundary.lengthFloat / deltaT))

        x, y = array(list(map(lambda s: self.boundary.get_point(s, evaluate=True), t))).T
        ax = self.figure.add_subplot(111)
        ax.axes.set_aspect('equal')
        ax.plot(x, y)

        self.points, = ax.plot([self.currentX], [self.currentY])

        self.figure.canvas.draw()
        self.figure.canvas.flush_events()


    # def iterate(self):
    #     [t, theta] = iterate(self.t, self.theta, self.boundary)
    #     self.t = t
    #     self.theta = theta

    #     [x, y] = self.boundary.get_point(t, evaluate=True)
    #     self.currentX = x
    #     self.currentY = y

    #     self.points.set_xdata(append(self.points.get_xdata(), x))
    #     self.points.set_ydata(append(self.points.get_ydata(), y))
    #     print(self.points.get_xdata(), self.points.get_ydata())

    #     self.figure.canvas.draw()
    #     self.figure.canvas.flush_events()


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

    