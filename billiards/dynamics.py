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
    [tangentX, tangentY] = boundary.get_tangent(dynamicState.t)

    # print(pointX, pointY, tangentX, tangentY)
    
    # Determine reflexion ray
    reflexionX = cos(pi - dynamicState.theta)*tangentX - sin(pi - dynamicState.theta)*tangentY
    reflexionY = sin(pi - dynamicState.theta)*tangentX + cos(pi - dynamicState.theta)*tangentY
    print("Reflecting for", reflexionX, reflexionY)
    reflexionRay = Ray((pointX, pointY), (pointX+reflexionX, pointY+reflexionY))
    
    # Determine intersections between reflexion ray and the boundary
    intersections = []
    for component in boundary.paths:
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
    nextPoint = closestIntersection["component"]["path"].get_point(nextRelativeS)
    nextTangent = closestIntersection["component"]["path"].get_tangent(nextRelativeS)
    print(nextPoint)
    print(nextTangent)
    # nextTheta = acos((nextTangentX*reflexionX + nextTangentY*reflexionY)/sqrt(nextTangentX**2 + nextTangentY**2)*sqrt(reflexionX**2 + reflexionY**2))
    nextTheta = determine_angle(Point2D(nextTangent), -reflexionRay.direction)
    print(nextAbsoluteS, nextTheta)

    print(timer.stats())
    return DynamicState({"t": nextAbsoluteS, "theta": nextTheta})

def firstIntersection(ray: Ray, path: SimplePath, plot=False):
    if plot: GraphicsMatPlotLib.plot_ray_and_path(ray, path)

    # Determinte transformation to transform ray into {x > 0}
    rotationAngle = -determine_angle(Point2D(1, 0), ray.direction)
    print(rotationAngle)

    newOrigin = Point2D(
        ray.source.x*cos(rotationAngle) - ray.source.y*sin(rotationAngle),
        ray.source.x*sin(rotationAngle) + ray.source.y*cos(rotationAngle)
    )
    print(newOrigin)

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
    newRay = Ray(newP1, newP2)
    print("ray", ray)
    print("newRay", newRay)
    if plot: GraphicsMatPlotLib.plot_ray_and_path(newRay, newPath)

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
        
        print(rayArgument)
        print(newRay.contains((rayArgument, 0)))

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