
import Splines
import Util


def checkParallel(curve, parallel, dist):
    """
    Measure an error between a curve and a proposed parallel
    """

    assert len(curve) == 8
    assert len(parallel) == 8
    error = 0
    for i in [1, 3, 5, 7]:
        a = i / 8.0
        p1 = Splines.splinePoint(curve, a)
        p2 = Splines.splinePoint(parallel, a)
        weight = Util.pyxLen(Splines.splineTangent(parallel, a)) / 8.0
        error += (Util.pyxLen(Util.pyxSub(p1, p2)) - dist)**2 * weight

    return error


def checkPen(curve, parallel, angle0, angle1, dist):
    """
    dito, with "pen parallels"
    """

    assert len(curve) == 8
    assert len(parallel) == 8
    error = 0
    for i in [1, 3, 5, 7]:
        a = i / 8.0
        
        angle = (angle0 * (1 - a) + angle1 * a)
        p1 = Splines.angledPoint(curve, a, angle, dist)
        p2 = Splines.splinePoint(parallel, a)

        error += Util.pyxLen(Util.pyxSub(p1, p2))**2

    return error


def curveParallel(c, dist, depth, dx0=None, dy0=None):
    """
    Construct a curve parallel in a given distance to a cubic bezier segment.

    c         curve segment (list of 8 float)
    dist      distance
    depth     recursion depth
    (dx0,dy0) suggested tangent to p0

    returns a list of curve segments
    """

    assert len(c) == 8
    assert isinstance(c[0], float)

    (x_0, y_0) = Splines.parallelPoint(c, 0, dist)
    (x_1, y_1) = Splines.parallelPoint(c, 0.5, dist)
    (x_2, y_2) = Splines.parallelPoint(c, 1, dist)

    if (dx0 is None):
        (dx0, dy0) = Splines.splineTangent(c, 0)

    (dx1, dy1) = Splines.splineTangent(c, 0.5)

    # Proposal: tangent given in p0 and p1

    proposal = Splines.directedSpline2(x_0, y_0, x_1, y_1, x_2, y_2,
                                       dx0, dy0, dx1, dy1)

    if depth > 5:
        return [proposal]

    error = checkParallel(c, proposal, abs(dist))

    if (error < 0.02):
        return [proposal]

    parts1 = Splines.splineSplit(c, 1 / 2.0)

    p11 = curveParallel(parts1[0], dist, depth + 1)
    p12 = curveParallel(parts1[1], dist, depth + 1)

    # try splits at 1/3 or 1/5

    if (depth < 2):

        parts2 = Splines.splineSplit(c, 1 / 3.0)

        p21 = curveParallel(parts2[0], dist, depth + 1)
        p22 = curveParallel(parts2[1], dist, depth + 1)

        if (len(p11) + len(p12) > len(p21) + len(p22)):
            return p21 + p22

        parts3 = Splines.splineSplit(c, 1 / 5.0)

        p31 = curveParallel(parts3[0], dist, depth + 1)
        p32 = curveParallel(parts3[1], dist, depth + 1)

        if (len(p11) + len(p12) > len(p31) + len(p32)):
            return p31 + p32

    return p11 + p12


def penParallel(c, dist, angle0, angle1, depth, dx0=None, dy0=None):
    """
    Construct a "pen parallel" to a cubic bezier segment.

    c         curve segment (list of 8 float)
    dist      distance
    depth     recursion depth
    angle0    pen angle at parameter 0
    angle1    pen angle at parameter 1
    (dx0,dy0) suggested tangent to p0

    returns a list of curve segments
    """

    assert len(c) == 8
    assert isinstance(c[0], float)

    angle03 = (angle0 * 2 + angle1    ) / 3.0
    angle06 = (angle0     + angle1 * 2) / 3.0

    p0 = Splines.angledPoint(c, 0,     angle0,  dist)
    p1 = Splines.angledPoint(c, 1/3.0, angle03, dist)
    p2 = Splines.angledPoint(c, 2/3.0, angle06, dist)
    p3 = Splines.angledPoint(c, 1,     angle1,  dist)

    proposal = Splines.naturalSpline([p0, p1, p2, p3])

    if depth > 5:
        return [proposal]

    error = checkPen(c, proposal, angle0, angle1, dist)

    if (error < 0.01):
        return [proposal]

    parts1 = Splines.splineSplit(c, 1 / 2.0)

    angleH = (angle0 + angle1) * 0.5

    p11 = penParallel(parts1[0], dist, angle0, angleH, depth + 1)
    p12 = penParallel(parts1[1], dist, angleH, angle1, depth + 1)

    # try splits at 1/3 or 1/5

    if (depth < 2):

        parts2 = Splines.splineSplit(c, 1 / 3.0)

        angleT = (angle0 + 2 * angle1) / 3.0

        p21 = penParallel(parts2[0], dist, angle0, angleT, depth + 1)
        p22 = penParallel(parts2[1], dist, angleT, angle1, depth + 1)

        if (len(p11) + len(p12) > len(p21) + len(p22)):
            return p21 + p22

        parts3 = Splines.splineSplit(c, 1 / 5.0)

        angleQ = (angle0 + 4 * angle1) / 5.0

        p31 = penParallel(parts3[0], dist, angle0, angleQ, depth + 1)
        p32 = penParallel(parts3[1], dist, angleQ, angle1, depth + 1)

        if (len(p11) + len(p12) > len(p31) + len(p32)):
            return p31 + p32

    return p11 + p12
