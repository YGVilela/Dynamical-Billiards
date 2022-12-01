from itertools import tee

from numpy import allclose, concatenate
from sympy import (EmptySet, Interval, Segment2D,
                   diff, parse_expr, symbols, floor)
from sympy.calculus.util import maximum, minimum

from billiards.utils.misc import to_expr
from billiards.utils.time import sharedTimer as timer


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

        self.startpoint = [
            float(self.expressionX.evalf(subs={t: self.t0})),
            float(self.expressionY.evalf(subs={t: self.t0}))
        ]
        self.endpoint = [
            float(self.expressionX.evalf(subs={t: self.t1})),
            float(self.expressionY.evalf(subs={t: self.t1}))
        ]

        self.poligonal = None
        self.poligonalDelta = 0

    def get_point(self, s, evaluate=False):
        if s < self.t0 or s > self.t1:
            raise Exception(
                f"Parameter {s} not in path's domain ({self.t0}, {self.t1})."
            )

        idGetPoint = timer.start_operation("get_point")
        t = symbols('t')
        x = self.expressionX.subs(t, s)
        y = self.expressionY.subs(t, s)

        if evaluate:
            x = float(x.evalf())
            y = float(y.evalf())

        timer.end_operation("get_point", idGetPoint)
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
        if self.poligonal is not None and deltaT >= self.poligonalDelta:
            return self.poligonal

        segments = []

        t0 = self.t0
        while t0 < self.t1:
            t1 = min(t0 + deltaT, self.t1)

            segment = Segment2D(self.get_point(t0), self.get_point(t1))
            if isinstance(segment, Segment2D):
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

    def from_json(dictionaire):
        return SimplePath(
            dictionaire["t0"],
            dictionaire["t1"],
            dictionaire["x"],
            dictionaire["y"],
        )

    def __str__(self):
        return "t -> (" + str(self.expressionX) + "," + \
            str(self.expressionY) + "), with t in (" + \
            str(self.t0) + "," + str(self.t1) + ")"

    def normal_disturb(self, function, domain):
        pathDomain = Interval(self.t0, self.t1)
        intersection = pathDomain.intersect(domain)
        if intersection == EmptySet:
            raise Exception("Function and path domain don't intersect.")

        newPaths = []

        if intersection.start > self.t0:
            t0 = self.t0
            t1 = intersection.start
            x = self.expressionX
            y = self.expressionY
            path = SimplePath(str(t0), str(t1), str(x), str(y))
            newPaths.append(path)

        t0 = intersection.start
        t1 = intersection.end
        x = self.expressionX + self.expressionDy * function
        y = self.expressionY - self.expressionDx * function
        path = SimplePath(str(t0), str(t1), str(x), str(y))
        newPaths.append(path)

        if intersection.end < self.t1:
            t0 = intersection.end
            t1 = self.t1
            x = self.expressionX
            y = self.expressionY
            path = SimplePath(str(t0), str(t1), str(x), str(y))
            newPaths.append(path)

        return newPaths


class ComposedPath:

    # Todo: Change this "periodic". It's not right
    def __init__(self, paths=[], periodic=True):
        self.t0 = parse_expr("0")
        self.t1 = parse_expr("0")
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

    def from_json(componentArray):
        paths = [
            SimplePath.from_json(component) for component in componentArray
        ]
        return ComposedPath(paths)

    def is_continuous(self):
        # https://docs.python.org/3/library/itertools.html#itertools.pairwise
        a, b = tee(self.paths)
        next(b, None)
        pairs = zip(a, b)

        for pair in pairs:
            firstPath = pair[0]["path"]
            lastPath = pair[1]["path"]

            if not allclose(firstPath.endpoint, lastPath.startpoint):
                return False

        return True

    def is_closed(self):
        if (not self.is_continuous()):
            return False

        firstPath = self.paths[0]["path"]
        lastPath = self.paths[-1]["path"]

        return allclose(firstPath.startpoint, lastPath.endpoint)

    def get_point(self, s, evaluate=False):
        if self.periodic and s > self.length:
            s = s % self.length

        for component in self.paths:
            startPoint = component["relative_t0"]
            endPoint = component["relative_t1"]
            if startPoint <= s <= endPoint:
                path = component["path"]
                relative_s = path.t0 + s - startPoint

                return path.get_point(relative_s, evaluate=evaluate)

        raise Exception("Can't evaluate path on t = " + str(s) +
                        " lower than 0 or greater than the length " +
                        str(self.length))

    def get_tangent(self, s, evaluate=False):
        if self.periodic and s > self.length:
            s = s % self.length

        for component in self.paths:
            startPoint = component["relative_t0"]
            endPoint = component["relative_t1"]
            if s >= startPoint and s <= endPoint:
                path = component["path"]
                relative_s = path.t0 + s - component["relative_t0"]

                return path.get_tangent(relative_s, evaluate=evaluate)

        raise Exception(
            "Can't evaluate path on t lower than 0 or greater than the length "
            + str(self.length)
        )

    def containing_box(self):
        xMin = yMin = xMax = yMax = None
        for component in self.paths:
            path = component["path"]
            curXMin, curYMin, curXMax, curYMax = path.containing_box()

            if xMin is None:
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

    def add_path(self, path: SimplePath):
        self.paths.append({
            "path": path,
            "relative_t0": self.t1,
            "relative_t1": self.t1 + path.length
        })
        self.t1 = self.t1 + path.length
        self.length = self.t1
        self.lengthFloat = float(self.length.evalf())

    def remove_path(self, index: int):
        removedComponent = self.paths.pop(index)
        removedLength = removedComponent["path"].length

        for i in range(index, len(self.paths)):
            self.paths[i]["relative_t0"] = \
                self.paths[i]["relative_t0"] - removedLength
            self.paths[i]["relative_t1"] = \
                self.paths[i]["relative_t1"] - removedLength

        self.t1 = self.t1 - removedLength
        self.length = self.t1
        self.lengthFloat = float(self.length.evalf())

    def update_path(self, index: int, newPath: SimplePath):
        oldPath = self.paths[index]["path"]
        lengthDifference = newPath.length - oldPath.length
        self.paths[index]["path"] = newPath
        self.paths[index]["relative_t1"] = \
            self.paths[index]["relative_t1"] + lengthDifference

        for i in range(index + 1, len(self.paths)):
            self.paths[i]["relative_t0"] = \
                self.paths[i]["relative_t0"] + lengthDifference
            self.paths[i]["relative_t1"] = \
                self.paths[i]["relative_t1"] + lengthDifference

        self.t1 = self.t1 + lengthDifference
        self.length = self.t1
        self.lengthFloat = float(self.length.evalf())

    def normal_disturb(self, function, domain):
        domain[0] = to_expr(domain[0])
        domain[1] = to_expr(domain[1])

        if domain[0] >= domain[1]:
            raise Exception(f"Invalid domain: {domain[0]} >= {domain[1]}")

        if domain[1] - domain[0] > self.length:
            raise Exception(
                "Invalid domain: domain's length larger than the path's.")

        rep0 = domain[0] % self.length
        rep1 = domain[1] % self.length
        functionAsExpr = parse_expr(function)

        # Disturbing interval doesn't cross the start/end point
        if rep0 < rep1 or rep1 == 0:
            if rep1 == 0:
                rep1 = self.length

            t = symbols("t")
            representantPeriod = floor(domain[0] / self.length)
            newTExpr = t + representantPeriod * self.length
            functionAsExpr = functionAsExpr.subs({t: newTExpr})
            domain[0] = rep0
            domain[1] = rep1

        else:
            repLength = domain[0] + (self.length - rep0)
            return self.normal_disturb(
                function, [str(domain[0]), str(repLength)]
            ).normal_disturb(
                function, [str(repLength), str(domain[1])]
            )

        domainAsInter = Interval(domain[0], domain[1],
                                 right_open=True, left_open=True)

        newPaths = []
        for component in self.paths:
            path = component["path"]
            relativeDomain = Interval(component["relative_t0"],
                                      component["relative_t1"],
                                      right_open=True,
                                      left_open=True)

            intersection = domainAsInter.intersect(relativeDomain)
            if intersection == EmptySet:
                newPaths.append([path])
                continue

            t = symbols("t")
            shiftValue = path.t0 - component["relative_t0"]
            shiftedT = t + shiftValue
            shiftedFunc = functionAsExpr.subs({t: shiftedT})
            shiftedDomain = Interval(intersection.start + shiftValue,
                                     intersection.end + shiftValue)

            disturbedPaths = path.normal_disturb(shiftedFunc, shiftedDomain)
            newPaths.append(disturbedPaths)

        disturbedCurve = ComposedPath(concatenate(newPaths))
        return disturbedCurve
