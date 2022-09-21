from itertools import tee
from sympy import parse_expr, symbols, diff, Segment2D, Interval, sqrt, acos, pi, simplify
from sympy.calculus.util import maximum, minimum
from billiards.time import sharedTimer as timer
from billiards.utils import to_expr

class PathParams:
    x: str
    y: str
    t0: str
    t1: str

    def __init__(self, dictionaire):
        self.x = dictionaire["x"]
        self.y = dictionaire["y"]
        self.t0 = dictionaire["t0"]
        self.t1 = dictionaire["t1"]

class SimplePath:
    def __init__(self, t0, t1, x, y):
        self.t0 = to_expr(t0)
        self.t1 = to_expr(t1)
        self.length = self.t1 - self.t0

        if self.length < 0:
            raise Exception("Can not instantiate a path with negative length!")

        self.lengthFloat = float(self.length.evalf())

        t = symbols('t')
        self.expressionX = parse_expr(x)
        self.expressionY = parse_expr(y)
        self.expressionDx = diff(self.expressionX, t)
        self.expressionDy = diff(self.expressionY, t)

        self.startpoint = [self.expressionX.evalf(subs={t: self.t0}), self.expressionY.evalf(subs={t: self.t0})]
        self.endpoint = [self.expressionX.evalf(subs={t: self.t1}), self.expressionY.evalf(subs={t: self.t1})]

        self.poligonal = None
        self.poligonalDelta = 0
    
    def get_point(self, s, evaluate=False):
        if s < self.t0 or s > self.t1:
            raise Exception("Parameter outside the path's domain.")

        t = symbols('t')
        x = self.expressionX.subs(t, s)
        y = self.expressionY.subs(t, s)

        if evaluate:
            return [float(x.evalf()), float(y.evalf())]
        else:
            return [x, y]

    def get_tangent(self, s, evaluate=False):
        if s < self.t0 or s > self.t1:
            raise Exception("Parameter outside the path's domain.")

        t = symbols('t')
        x = self.expressionDx.subs(t, s)
        y = self.expressionDy.subs(t, s)

        if evaluate:
            return [float(x.evalf()), float(y.evalf())]
        else:
            return [x, y]

    def poligonize(self, deltaT=.1):
        if self.poligonal != None and deltaT >= self.poligonalDelta:
            return self.poligonal

        segments = []

        t0 = self.t0
        while t0 < self.t1:
            t1 = min(t0 + deltaT, self.t1)

            segment = Segment2D(self.get_point(t0), self.get_point(t1))
            if type(segment) == Segment2D:
                segments.append(segment)

            t0 = t1

        self.poligonal = segments
        self.poligonalDelta = deltaT

        return segments

    def containing_box(self):
        t = symbols("t")
        xMin = minimum(self.expressionX, t, Interval(self.t0, self.t1))
        xMax = maximum(self.expressionX, t, Interval(self.t0, self.t1))
        yMin = minimum(self.expressionY, t, Interval(self.t0, self.t1))
        yMax = maximum(self.expressionY, t, Interval(self.t0, self.t1))

        return xMin, yMin, xMax, yMax

    def is_on_domain(self, t):
        return Interval(self.t0, self.t1).contains(t)

    def to_json(self):
        return {
            "x": str(self.expressionX),
            "y": str(self.expressionY),
            "t0": str(self.t0),
            "t1": str(self.t1)
        }

class ComposedPath:

    def __init__(self, paths, periodic=True):
        self.t0 = parse_expr("0")
        self.t1 = 0
        self.paths = []
        self.periodic = periodic

        for path in paths:
            self.paths.append({
                "path": path,
                "relative_t0": self.t1,
                "relative_t1": self.t1 + path.length
            })
            self.t1 = self.t1 + path.length

        self.length = self.t1
        self.lengthFloat = float(self.length.evalf())

    def to_json(self):
        return [component["path"].to_json() for component in self.paths]

    def is_continuous(self):
        # understand that! https://docs.python.org/3/library/itertools.html#itertools.pairwise
        a, b = tee(self.paths)
        next(b, None)
        pairs = zip(a, b)

        t = symbols("t")
        for pair in pairs:
            firstPath = pair[0]["path"]
            lastPath = pair[1]["path"]

            if firstPath.endpoint != lastPath.startpoint:
                return False

        return True

    def is_closed(self):
        if(not self.is_continuous()):
            return False

        firstPath = self.paths[0]["path"]
        lastPath = self.paths[-1]["path"]

        return firstPath.endpoint != lastPath.startpoint

    def get_point(self, s, evaluate = False):
        if self.periodic:
            s = s%self.length

        for currentPath in self.paths:
            # Fix that. The equality on both sides may lead to bizarre behaviours (?)
            if s >= currentPath["relative_t0"] and s <= currentPath["relative_t1"]:
                path = currentPath["path"]
                relative_s = path.t0 + s - currentPath["relative_t0"]
                
                return path.get_point(relative_s, evaluate=evaluate)

        raise Exception("Can't evaluate path on t = " + str(s) + "lower than 0 or greater than the length " + str(self.length))

    def get_tangent(self, s, evaluate=False):
        if self.periodic:
            s = s%self.length

        for component in self.paths:
            # Fix that. The equality on both sides may lead to bizarre behaviours (?)
            if s >= component["relative_t0"] and s <= component["relative_t1"]:
                path = component["path"]
                relative_s = path.t0 + s - component["relative_t0"]
                
                return path.get_tangent(relative_s, evaluate=evaluate)

        raise Exception("Can't evaluate path on t lower than 0 or greater than the length " + str(self.length))

    def containing_box(self):
        xMin = yMin = xMax = yMax = None
        for component in self.paths:
            path = component["path"]
            curXMin, curYMin, curXMax, curYMax = path.containing_box()

            if xMin == None:
                xMin = curXMin
                yMin = curYMin
                xMax = curXMax
                yMax = curYMax

                continue
            
            if xMin > curXMin:
                xMin = curXMin
            if yMin > curYMin:
                yMin = curYMin
            if xMax < curXMax:
                xMax = curXMax
            if yMax < curYMax:
                yMax = curYMax

        return xMin, yMin, xMax, yMax

'''Determines the angle between two vectors'''
def determine_angle(v1, v2):
    idAngleDetermination = timer.start_operation("determine_angle")

    innerProduct = v1.x*v2.x+v1.y*v2.y
    normV1 = sqrt(v1.x*v1.x+v1.y*v1.y)
    normV2 = sqrt(v2.x*v2.x+v2.y*v2.y)

    thetaCandidate = acos(innerProduct/normV1*normV2)

    # v1.x*v2.y - v2.x*v1.y = normV1*normV2*sin(theta)
    if v1.x*v2.y - v2.x*v1.y >= 0:
        theta = thetaCandidate
    else:
        theta = 2*pi-thetaCandidate

    simplified = simplify(theta)

    timer.end_operation("determine_angle", idAngleDetermination)
    return simplified
