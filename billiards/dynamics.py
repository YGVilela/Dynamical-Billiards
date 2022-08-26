from sympy import symbols, cos, sin, pi, acos, sqrt, Ray, EmptySet, nsolve, Segment2D, Point2D, solve, solveset, Interval, atan, SymmetricDifference, FiniteSet, Eq
from multiprocessing import Pool
from billiards.geometry import SimplePath
from billiards.time import sharedTimer as timer
from billiards.utils import doIntersect


def iterate(s0, theta0, boundaries, paralelize=False):
    [pointX, pointY] = boundaries.get_point(s0)
    point = Point2D(pointX, pointY)
    [tangentX, tangentY] = boundaries.get_tangent(s0)

    # print(pointX, pointY, tangentX, tangentY)
    
    # Apply rotation of pi - theta to the tangent vector to get the reflexion direction
    reflexionX = cos(pi - theta0)*tangentX - sin(pi - theta0)*tangentY
    reflexionY = sin(pi - theta0)*tangentX + cos(pi - theta0)*tangentY

    # Determine reflexion ray
    reflexionRay = Ray((pointX, pointY), (pointX+reflexionX, pointY+reflexionY))
    
    # Determine intersections between reflexion ray and the boundary
    intersections = []
    t, t1 = symbols("t, t1")
    for component in boundaries.paths:
        currentPath = component["path"]

        # Get approximate intersections
        print("Calculating intersection")
        idSolve = timer.start_operation("solve")
        currentIntersection = firstIntersection(reflexionRay, currentPath)
        timer.end_operation("solve", idSolve)

        if currentIntersection != None:
            intersections.append({"t": currentIntersection, "component": component})

    if(len(intersections) == 0):
        raise Exception("The trajectory line doesn't intersect the curve again!")

    # Get the closest intersection
    closestIntersection  = min(intersections, key=lambda inter: float(inter["t"].evalf()))
    print("closest of all", closestIntersection)

    # Determine next intersection point
    nextRelativeS = closestIntersection["t"] - closestIntersection["component"]["path"].t0
    nextAbsoluteS = nextRelativeS + closestIntersection["component"]["relative_t0"]
    print("next s", nextRelativeS, nextAbsoluteS)

    # Determine next incidence angle
    [nextTangentX, nextTangentY] = closestIntersection["component"]["path"].get_tangent(nextAbsoluteS)
    nextTheta = acos((nextTangentX*reflexionX + nextTangentY*reflexionY)/sqrt(nextTangentX**2 + nextTangentY**2)*sqrt(reflexionX**2 + reflexionY**2))

    print(nextAbsoluteS, nextTheta)

    print(timer.stats())
    return nextAbsoluteS, nextTheta

def firstIntersection(ray: Ray, path: SimplePath):
    plot(ray, path)

    # Determinte transformation to transform ray into {x > 0}
    rotationAngle = pi-atan(ray.slope)
    print(rotationAngle)

    newOrigin = Point2D(
        ray.p1.x*cos(rotationAngle) - ray.p1.y*sin(rotationAngle),
        ray.p1.x*sin(rotationAngle) + ray.p1.y*cos(rotationAngle)
    )
    px, py = symbols("x, y")
    transformX = cos(rotationAngle)*px - sin(rotationAngle)*py - newOrigin.x
    transformY = sin(rotationAngle)*px + cos(rotationAngle)*py - newOrigin.y
    print(transformX)
    print(transformY)

    # Apply transformation to path
    newPath = SimplePath(
        str(path.t0),
        str(path.t1),
        str(transformX.subs({px: path.expressionX, py: path.expressionY})),
        str(transformY.subs({px: path.expressionX, py: path.expressionY})),
    )

    print(newPath.expressionX)
    print(newPath.expressionY)

    newP1 = (transformX.subs({px: ray.p1.x, py: ray.p1.y}), transformY.subs({px: ray.p1.x, py: ray.p1.y}))
    newP2 = (transformX.subs({px: ray.p2.x, py: ray.p2.y}), transformY.subs({px: ray.p2.x, py: ray.p2.y}))
    plot(Ray(newP1, newP2), newPath)

    # Get point where y = 0, i.e., intersection between path and the ray
    t = symbols("t")
    intersection = solveset(newPath.expressionY, t, domain=Interval(newPath.t0, newPath.t1))
    print(intersection)

    # If no intersection, return None
    if intersection == EmptySet:
        return None

    # If intersection isn't a finite set, raise exception
    if type(intersection) != FiniteSet:
        raise Exception("Only finite intersection implemented so far.")

    # Determine first intersection that isn't the ray source
    firstIntersection = None
    smallestRayArgument = 0
    for inter in intersection.args:
        rayArgument = newPath.expressionX.subs({t: inter})
        
        # Ignore intersections before or at the ray source
        if Eq(rayArgument, 0) or rayArgument < 0:
            continue

        if firstIntersection == None:
            firstIntersection = inter
            smallestRayArgument = rayArgument
        elif smallestRayArgument > rayArgument:
            firstIntersection = inter
            smallestRayArgument = rayArgument

    return firstIntersection

def plot(ray: Ray, path: SimplePath):
    from matplotlib import pyplot as plt
    from numpy import linspace, array#, append
    from math import ceil

    t = linspace(0, path.lengthFloat, ceil(path.lengthFloat / 0.1))

    x, y = array(list(map(lambda s: path.get_point(s, evaluate=True), t))).T
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.axes.set_aspect('equal')

    ax.plot(x, y)
    ax.plot([float(ray.p1.x.evalf()), float((ray.p2.x).evalf())], [float(ray.p1.y.evalf()), float((ray.p2.y).evalf())])
    plt.show()
    

    
