from sympy import symbols, cos, sin, pi, acos, sqrt, Ray, EmptySet, nsolve, Segment2D, Point2D, solve, solveset, Interval, atan, SymmetricDifference, FiniteSet, Eq, parse_expr
from multiprocessing import Pool
from billiards.geometry import ComposedPath, SimplePath, determine_angle
from billiards.time import sharedTimer as timer
# from billiards.utils import doIntersect
from billiards.graphics import GraphicsMatPlotLib

class DynamicState:
    def __init__(self, dictionaire):
        self.t = dictionaire["t"]
        self.theta = dictionaire["theta"]

        if type(self.t) == str:
            self.t = parse_expr(self.t)

        if type(self.theta) == str:
            self.theta = parse_expr(self.theta)

def iterate(dynamicState: DynamicState, boundary: ComposedPath):
    [pointX, pointY] = boundary.get_point(dynamicState.t)
    print("Current point", pointX, pointY)
    [tangentX, tangentY] = boundary.get_tangent(dynamicState.t)
    print("Current tangent", tangentX, tangentY)
    
    # Determine reflexion ray
    reflexionX = cos(pi - dynamicState.theta)*tangentX - sin(pi - dynamicState.theta)*tangentY
    reflexionY = sin(pi - dynamicState.theta)*tangentX + cos(pi - dynamicState.theta)*tangentY
    reflexionRay = Ray((pointX, pointY), (pointX+reflexionX, pointY+reflexionY))
    print("Reflextion ray", reflexionRay)
    
    # Determine intersections between reflexion ray and the boundary
    intersections = []
    for component in boundary.paths:
        currentPath = component["path"]

        # Get first intersection with every path
        print("Calculating intersection with", currentPath.expressionX, currentPath.expressionY)
        idSolve = timer.start_operation("solve")
        currentIntersection = first_intersection(reflexionRay, currentPath)
        timer.end_operation("solve", idSolve)

        if currentIntersection != None:
            intersections.append({"t": currentIntersection, "component": component})

    # If there's no intersection, raise exception
    if(len(intersections) == 0):
        raise Exception("The trajectory line doesn't intersect the curve again!")

    # Get the closest intersection
    closestIntersection  = min(intersections, key=lambda inter: float(inter["t"].evalf()))
    print("Closest intersection", closestIntersection)

    # Determine next intersection point
    nextRelativeS = closestIntersection["t"] - closestIntersection["component"]["path"].t0
    nextAbsoluteS = nextRelativeS + closestIntersection["component"]["relative_t0"]
    print("Next s", nextRelativeS, nextAbsoluteS)

    # Determine next incidence angle
    nextTangent = closestIntersection["component"]["path"].get_tangent(nextRelativeS)
    print("Next tangent", nextTangent)

    nextTheta = determine_angle(Point2D(nextTangent), -reflexionRay.direction)
    print("Next theta", nextTheta)

    print(timer.stats())
    return DynamicState({"t": nextAbsoluteS, "theta": nextTheta})

def first_intersection(ray: Ray, path: SimplePath, plot=False):
    if plot: GraphicsMatPlotLib.plot_ray_and_path(ray, path)

    # Determinte transformation to transform ray into {x > 0}
    rotationAngle = -determine_angle(Point2D(1, 0), ray.direction)
    print("Rotation angle", rotationAngle)

    newOrigin = Point2D(
        ray.source.x*cos(rotationAngle) - ray.source.y*sin(rotationAngle),
        ray.source.x*sin(rotationAngle) + ray.source.y*cos(rotationAngle)
    )
    print("New origin", newOrigin)

    px, py = symbols("x, y")
    transformX = cos(rotationAngle)*px - sin(rotationAngle)*py - newOrigin.x
    transformY = sin(rotationAngle)*px + cos(rotationAngle)*py - newOrigin.y
    print("Transformation", transformX, transformY)

    # Apply transformation to path and ray
    newPath = SimplePath(
        str(path.t0),
        str(path.t1),
        str(transformX.subs({px: path.expressionX, py: path.expressionY})),
        str(transformY.subs({px: path.expressionX, py: path.expressionY})),
    )
    print("New path", newPath.expressionX, newPath.expressionY)

    newP1 = (transformX.subs({px: ray.p1.x, py: ray.p1.y}), transformY.subs({px: ray.p1.x, py: ray.p1.y}))
    newP2 = (transformX.subs({px: ray.p2.x, py: ray.p2.y}), transformY.subs({px: ray.p2.x, py: ray.p2.y}))
    newRay = Ray(newP1, newP2)
    print("New ray", newRay)
    if plot: GraphicsMatPlotLib.plot_ray_and_path(newRay, newPath)

    # Get the roots of y's expression, i.e., intersection between path and the ray
    intersection = find_roots(newPath.expressionY, Interval(newPath.t0, newPath.t1))
    print("Intersections", intersection)

    # If no intersection, return None
    if len(intersection) == 0:
        return None

    # Determine first intersection that isn't the ray source
    firstIntersection = None
    smallestRayArgument = 0
    t = symbols('t')
    for inter in intersection:
        # Ray argument equals the path's x
        rayArgument = newPath.expressionX.subs({t: inter})

        # Ignore intersections before or at the ray source
        if Eq(rayArgument, 0) or not newRay.contains((rayArgument, 0)):
            continue

        if firstIntersection == None:
            firstIntersection = inter
            smallestRayArgument = rayArgument
        elif smallestRayArgument > rayArgument:
            firstIntersection = inter
            smallestRayArgument = rayArgument

    return firstIntersection

def find_roots(expr, interval):
    t = symbols("t")

    roots = solveset(expr, t, domain=interval)
    print("roots of", expr, roots)

    if roots == EmptySet:
        return []

    # If intersection isn't a finite set, raise exception
    if type(roots) != FiniteSet:
        raise Exception("Only finite intersection implemented so far.")

    return roots.args

# def iterate_old(s0, theta0, boundaries, paralelize=False):
#     [pointX, pointY] = boundaries.get_point(s0)
#     point = Point2D(pointX, pointY)
#     [tangentX, tangentY] = boundaries.get_tangent(s0)

#     # print(pointX, pointY, tangentX, tangentY)
    
#     # Apply rotation of pi - theta to the tangent vector to get the reflexion direction
#     reflexionX = cos(pi - theta0)*tangentX - sin(pi - theta0)*tangentY
#     reflexionY = sin(pi - theta0)*tangentX + cos(pi - theta0)*tangentY

#     # Determine reflexion segment
#     reflexionRay = Ray((pointX, pointY), (pointX+reflexionX, pointY+reflexionY))
#     xMin, yMin, xMax, yMax = boundaries.containing_box()
#     boxSegments = [
#         Segment2D((xMin, yMin), (xMin, yMax)),
#         Segment2D((xMin, yMax), (xMax, yMax)),
#         Segment2D((xMax, yMax), (xMax, yMin)),
#         Segment2D((xMax, yMin), (xMin, yMin)),
#         ]
    
#     boxIntersection = None
#     for segment in boxSegments:
#         idInter = timer.start_operation("intersection")
#         approxObject = reflexionRay.intersect(segment)
#         timer.end_operation("intersection", idInter) 

#         if approxObject == EmptySet:
#             continue
#         if type(approxObject) == Segment2D:
#             if approxObject.p1.distance(point) > approxObject.p2.distance(point):
#                 boxIntersection = approxObject.p1
#             else:
#                 boxIntersection = approxObject.p2
#             continue
#         if approxObject.args[0] != point:
#             boxIntersection = approxObject.args[0]

#     reflexionSegment = Segment2D((pointX, pointY), boxIntersection)

#     # Determine intersections between reflexion segment and the boundary
#     intersections = []
#     t, t1 = symbols("t, t1")
#     for component in boundaries.paths:
#         currentPath = component["path"]
#         # print(currentPath.expressionX, currentPath.expressionY)

#         # Get approximate intersections
#         idInter = timer.start_operation("segmentation")
#         segments = currentPath.poligonize(deltaT=0.1)
#         timer.end_operation("segmentation", idInter)

#         approxIntersections = []
#         # This isn't performing well
#         if paralelize:
#             pool = Pool()
#             idInter = timer.start_operation("intersection")
#             # Edit this to check if the segments intersect beforehand
#             approxIntersections = pool.map(reflexionSegment.intersect, segments)
#             timer.end_operation("intersection", idInter)
#         else:
#             for segment in segments:
#                 if doIntersect(reflexionSegment.p1, reflexionSegment.p2, segment.p1, segment.p2):
#                     idInter = timer.start_operation("intersection")
#                     approxObject = reflexionSegment.intersect(segment)
#                     approxIntersections.append(approxObject)
#                     timer.end_operation("intersection", idInter)    

#         closestApproxInter = None
#         minDistance = 0
#         for approxObject in approxIntersections:
#             approxPoint = None
#             if approxObject == EmptySet:
#                 continue
#             if type(approxObject) == Segment2D:
#                 approxPoint = approxObject.p1
#             else:
#                 approxPoint = approxObject.args[0]

#             currentDistance = approxPoint.distance(point)
#             print(currentDistance, float(currentDistance.evalf()), minDistance, currentDistance > 0, closestApproxInter == None)
#             if currentDistance > 0 and (closestApproxInter == None or minDistance > currentDistance):
#                 approxX = float(approxPoint.x.evalf())
#                 approxY = float(approxPoint.y.evalf())
#                 closestApproxInter = (approxX, approxY)
#                 minDistance = currentDistance

#             print(closestApproxInter)

#         if closestApproxInter == None:
#             continue

#         print("Calculating intersection")
#         idSolve = timer.start_operation("solve")
#         intersection = solve(
#             [pointX+t1*reflexionX - currentPath.expressionX, pointY+t1*reflexionY - currentPath.expressionY],
#             [t, t1],
#             # closestApproxInter,
#             dict=True)
#         # print("closestApprox", closestApproxInter, "intersection", intersection)
#         timer.end_operation("solve", idSolve)

#         # print(intersection)
#         if intersection == EmptySet:
#             continue

#         print("intersections", intersection)
#         nonTrivialIntersections = list(
#             filter(
#                 lambda inter: inter[t1].is_real and inter[t1] > 0 and inter[t].is_real and currentPath.is_on_domain(inter[t]),
#                 intersection
#             )
#         )
#         # print(nonTrivialIntersections)
#         if nonTrivialIntersections.__len__() == 0:
#             continue

#         print("non trivial", nonTrivialIntersections)
#         closestIntersection = min(nonTrivialIntersections, key=lambda inter: inter[t1])
#         closestIntersection["component"] = component
#         print("closest", closestIntersection)
#         intersections.append(closestIntersection)

#     if(len(intersections) == 0):
#         raise Exception("The trajectory line doesn't intersect the curve again!")

#     # Get the closest intersection
#     closestIntersection  = min(intersections, key=lambda inter: inter[t1])
#     print("closest of all", closestIntersection)

#     # Determine next intersection point
#     nextRelativeS = closestIntersection[t] - closestIntersection["component"]["path"].t0
#     nextAbsoluteS = nextRelativeS + closestIntersection["component"]["relative_t0"]
#     print("next s", nextRelativeS, nextAbsoluteS)

#     # Determine next incidence angle
#     [nextTangentX, nextTangentY] = closestIntersection["component"]["path"].get_tangent(nextAbsoluteS)
#     nextTheta = acos((nextTangentX*reflexionX + nextTangentY*reflexionY)/sqrt(nextTangentX**2 + nextTangentY**2)*sqrt(reflexionX**2 + reflexionY**2))

#     print(nextAbsoluteS, nextTheta)

#     print(timer.stats())
#     return nextAbsoluteS, nextTheta