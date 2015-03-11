
import pyx
import math
import Splines


def roundJoin(p1, p2, x, y, dist):
    """
    return a circle segment with radius dist about (x, y) joining paths 
    p1 and p2
    """

    (x0, y0) = p1.atend()
    (x1, y1) = p2.atbegin()

    (dx0, dy0) = (pyx.unit.topt(x - x0), pyx.unit.topt(y - y0))
    (dx1, dy1) = (pyx.unit.topt(x - x1), pyx.unit.topt(y - y1))

    alpha = math.atan2(dy0, dx0)
    delta = math.atan2(dy1, dx1)

    angle = delta - alpha

    beta = (alpha + delta) * 0.5

    if (abs(angle) < math.pi / 2):
        
        p = []

        for stop in range(0,4):

            beta = alpha + angle/3.0*stop 

            (x1, y1) = (x - math.cos(beta) * abs(dist),
                        y - math.sin(beta) * abs(dist))

            p.append((x1, y1))

        A = Splines.naturalSpline(p)

        return pyx.path.curve(*A)

    else:

        p = []

        for stop in range(0,4):

            beta = alpha + angle/6.0*stop 

            (x1, y1) = (x - math.cos(beta) * abs(dist),
                        y - math.sin(beta) * abs(dist))

            p.append((x1, y1))

        A = Splines.naturalSpline(p)

        p = []

        for stop in range(3,7):

            beta = alpha + angle/6.0*stop 

            (x1, y1) = (x - math.cos(beta) * abs(dist),
                        y - math.sin(beta) * abs(dist))

            p.append((x1, y1))

        B = Splines.naturalSpline(p)

        c1 = pyx.path.curve(*A)
        c2 = pyx.path.curve(*B)

        return c1 << c2


def hollowJoin(p1, p2, x, y, dist):
    (x0, y0) = p1.atend()
    (x3, y3) = p2.atbegin()

    (x0, y0) = (pyx.unit.topt(x0), pyx.unit.topt(y0))
    (x3, y3) = (pyx.unit.topt(x3), pyx.unit.topt(y3))

    (dx0, dy0) = (x0 - x, y0 - y)
    (dx3, dy3) = (x3 - x, y3 - y)

    mangle = ((x0 + x3) * 0.5, (y0 + y3) * 0.5)

    alpha = math.atan2(dy0, dx0)
    delta = math.atan2(dy3, dx3)

    beta = (alpha * 2.0 + delta) / 3.0
    gamma = (alpha + delta * 2.0) / 3.0

    if alpha < delta:
        dist = -dist

    (x1, y1) = (mangle[0] - math.cos(gamma) * dist,
                mangle[1] - math.sin(gamma) * dist)
    (x2, y2) = (mangle[0] - math.cos(beta) * dist,
                mangle[1] - math.sin(beta) * dist)

    return pyx.path.curve(
        *Splines.naturalSpline([(x0, y0), (x1, y1), (x2, y2), (x3, y3)])
    )


def miterJoin(p1, p2, dist):
    """
    Extend tangents of two paths for a certain distance, cut them in the
    intersection point. p1 is pointing outwards, p2 inwards.
    """

    t1 = p1.tangent(p1.end(), dist)
    t2 = p2.tangent(p2.begin(), -dist)

    intersections = t1.intersect(t2)

    if (len(intersections[0]) > 0):

        segment1 = t1.split(intersections[0])[0]
        segment2 = t2.split(intersections[1])[0]
        segment = segment1.joined(segment2.reversed())
        return segment

    else:
        return t1.joined(t2.reversed())


def joinPaths(joinType, p1, p2, x, y, dist):

    if (joinType == 'bevel'):

        (x0, y0) = p1.atend()
        (x1, y1) = p2.atbegin()

        return pyx.path.line(x0, y0, x1, y1)

    if (joinType == 'miter'):

        return miterJoin(p1, p2, abs(dist * 0.5))

    if (joinType == 'round'):

        return roundJoin(p1, p2, x, y, dist)

    if (joinType == 'hollow'):

        return hollowJoin(p1, p2, x, y, dist)
