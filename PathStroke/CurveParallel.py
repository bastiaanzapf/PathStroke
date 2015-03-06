
from pyx import *

from numpy import *
from numpy.linalg import *
import Splines
from Util import *


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
        weight = pyxLen(Splines.splineTangent(parallel, a)) / 8.0
        error += (pyxLen(pyxSub(p1, p2)) - dist)**2 * weight

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
