
#
# Some spline tricks. This is very chaotic.
#
# http://graphics.pixar.com/people/derose/publications/CubicClassification/paper.pdf

import math
import numpy

B = numpy.mat([[-1, 3, -3, 1],
               [3, -6, 3, 0],
               [-3, 3, 0, 0],
               [1, 0, 0, 0]])

DB = numpy.mat([[-3,  6, -3],
                [9, -12, 3],
                [-9,  6, 0],
                [3,  0, 0]]).transpose()

DDB = numpy.mat([[-6, 6],
                 [18, -12],
                 [-18,  6],
                 [6,  0]]).transpose()


def splinePoint(c, at):

    v = numpy.mat([at**3, at**2, at, 1])

    x = numpy.mat(c[0::2]).transpose()
    x = v * B * x
    y = numpy.mat(c[1::2]).transpose()
    y = v * B * y

    return (float(x), float(y))


def splineTangent(c, at):

    v = numpy.mat([at**2, at, 1])

    x = numpy.mat(c[0::2]).transpose()
    dx = v * DB * x
    y = numpy.mat(c[1::2]).transpose()
    dy = v * DB * y

    return (float(dx), float(dy))


def parallelPoint(c, at, dist):
    """
    return the point at distance dist normal to c in parameter at
    """
    assert len(c) == 8
    assert isinstance(dist, (int, float))

    (x, y) = splinePoint(c, at)

    (dx, dy) = splineTangent(c, at)

    if (dx**2 + dy**2 != 0):
        f = 1 / math.sqrt(dx**2 + dy**2)
    else:
        f = 0

    normal = (-dy * f, dx * f)

    return (x + dist * normal[0], y + dist * normal[1])

def angledPoint(c, at, angle, dist):
    """
    return the point at distance dist at given angle in parameter at
    """
    assert len(c) == 8
    assert isinstance(dist, (int, float))

    (x, y) = splinePoint(c, at)
    (dx, dy) = splineTangent(c, at)

    return (x + dist * math.cos(angle), 
            y + dist * math.sin(angle))

def bernshteinValues(c):
    v = numpy.mat([c**3, c**2, c, 1])
    return v * B


def bernshteinDerivatives(c):
    v = numpy.mat([c**2, c, 1])
    return v * DB

natSpline = numpy.array(numpy.zeros((4, 4)))

for i in range(0, 4):
    natSpline[i] = bernshteinValues(i / 3.0)

dirSpline = numpy.array(numpy.zeros((4, 4)))

for i in range(0, 3):
    dirSpline[i] = bernshteinValues(i / 2.0)

dirSpline[3] = bernshteinDerivatives(0)


def naturalSpline(p):
    """
    Return control points of a "natural spline"
    """
    assert len(p) == 4
    assert len(p[0]) == 2
    assert len(p[1]) == 2
    assert len(p[2]) == 2
    assert len(p[3]) == 2

    b1 = numpy.array([p[0][0], p[1][0], p[2][0], p[3][0]])
    b2 = numpy.array([p[0][1], p[1][1], p[2][1], p[3][1]])

    x = numpy.linalg.solve(natSpline, b1)
    y = numpy.linalg.solve(natSpline, b2)

    return (x[0], y[0], x[1], y[1],
            x[2], y[2], x[3], y[3])

D = numpy.matrix(numpy.zeros((8, 8)))

for i in range(0, 3):
    D[i, 0:4] = bernshteinValues(i / 2.0)
    D[i + 4, 4:8] = bernshteinValues(i / 2.0)


def directedMatrix(a, b, c, d, e, f):

    A = D.copy()

    bep = bernshteinDerivatives(0)
    A[3, 0:4] = b * bep
    A[3, 4:8] = -a * bep

    bep = bernshteinDerivatives(1)
    A[7, 0:4] = d * bep
    A[7, 4:8] = -c * bep

    bep = bernshteinDerivatives(0.5)

    A[3, 0:4] += f * bep * 0.5
    A[3, 4:8] += -e * bep * 0.5

    A[7, 0:4] += f * bep * 0.5
    A[7, 4:8] += -e * bep * 0.5

    return A


def directedMatrix2(a, b, c, d):

    A = D.copy()

    bep = bernshteinDerivatives(0)
    A[3, 0:4] = b * bep
    A[3, 4:8] = -a * bep

    bep = bernshteinDerivatives(0.5)
    A[7, 0:4] = d * bep
    A[7, 4:8] = -c * bep

    return A


def directedSpline(p, a, b, c, d, e, f):
    """
    Return control points of a Spline through three points p, with
    set tangents

    in p0: (a,b)
    in p1: (e,f)
    in p2: (c,d)

    there are many instances for which the result is defined but bizarre,
    so use with caution
    """

    assert len(p) == 3
    assert len(p[0]) == 2
    assert len(p[1]) == 2
    assert len(p[2]) == 2
    assert isinstance(a, float)
    assert isinstance(b, float)
    assert isinstance(c, float)
    assert isinstance(d, float)

    D = directedMatrix(a, b, c, d, e, f)

    assert isinstance(D, numpy.matrix)

    b = numpy.matrix([[p[0][0]], [p[1][0]], [p[2][0]], [0],
                      [p[0][1]], [p[1][1]], [p[2][1]], [0]])

    x = numpy.linalg.solve(D, b)

    return (float(p[0][0]), float(p[0][1]),
            float(x[1]), float(x[5]),
            float(x[2]), float(x[6]),
            float(p[2][0]), float(p[2][1]))


def directedSpline2(x0, y0, x1, y1, x2, y2, a, b, c, d):
    """
    Return control points of a Spline through three points (xn,yn), with
    set tangents

    in (x0,y0): (a,b)
    in (x1,y1): (c,d)

    there are many instances for which the result is defined but bizarre,
    so use with caution
    """
    assert(isinstance(x0, float))
    assert(isinstance(y0, float))
    assert(isinstance(x1, float))
    assert(isinstance(y1, float))
    assert(isinstance(x2, float))
    assert(isinstance(y2, float))
    assert(isinstance(a, float))
    assert(isinstance(b, float))
    assert(isinstance(c, float))
    assert(isinstance(d, float))

    D = directedMatrix2(a, b, c, d)

    assert isinstance(D, numpy.matrix)

    v = numpy.matrix([[x0], [x1], [x2], [0],
                      [y0], [y1], [y2], [0]])

    x = numpy.linalg.solve(D, v)

    return (float(x0), float(y0),
            float(x[1]), float(x[5]),
            float(x[2]), float(x[6]),
            float(x2), float(y2))


def splineSplit(curve, parameter=0.5):
    """
    De Casteljau's algorithm
    """
    assert len(curve) == 8
    p0 = (curve[0], curve[1])
    p1 = (curve[2], curve[3])
    p2 = (curve[4], curve[5])
    p3 = (curve[6], curve[7])

    p4 = (p0[0] + (p1[0] - p0[0]) * parameter,
          p0[1] + (p1[1] - p0[1]) * parameter)
    p5 = (p1[0] + (p2[0] - p1[0]) * parameter,
          p1[1] + (p2[1] - p1[1]) * parameter)
    p6 = (p2[0] + (p3[0] - p2[0]) * parameter,
          p2[1] + (p3[1] - p2[1]) * parameter)

    p7 = (p4[0] * (1 - parameter) + p5[0] * parameter,
          p4[1] * (1 - parameter) + p5[1] * parameter)
    p8 = (p5[0] * (1 - parameter) + p6[0] * parameter,
          p5[1] * (1 - parameter) + p6[1] * parameter)
    p9 = (p7[0] * (1 - parameter) + p8[0] * parameter,
          p7[1] * (1 - parameter) + p8[1] * parameter)

    newcurves = [[p0[0], p0[1],
                  p4[0], p4[1],
                  p7[0], p7[1],
                  p9[0], p9[1]],
                 [p9[0], p9[1],
                  p8[0], p8[1],
                  p6[0], p6[1],
                  p3[0], p3[1]]]

    return newcurves

def splineJoin(curve1, curve2):
    """
    De casteljau's algorithm in reverse: join two adjacent splines.
    This only gives sensible results when the curves actually fit.
    """
    assert len(curve1) == 8
    assert len(curve2) == 8

    p10 = (curve1[0], curve1[1])
    p11 = (curve1[2], curve1[3])
    p12 = (curve1[4], curve1[5])
    p13 = (curve1[6], curve1[7])

    p20 = (curve2[0], curve2[1])
    p21 = (curve2[2], curve2[3])
    p22 = (curve2[4], curve2[5])
    p23 = (curve2[6], curve2[7])

    if math.hypot(p13[0] - p20[0], p13[1] - p20[1]) > 1e-10:
        raise Exception("curve 2 must start where curve 1 ends")

    a = p12[0] - p13[0]
    b = p20[0] - p21[0]
    c = p12[1] - p13[1]
    d = p20[1] - p21[1]

    ratio1 = (math.hypot(a,c) / math.hypot(b,d))

    parameter1 = (ratio1 + 1.0) / ratio1

    ratio2 = 1.0 / ratio1

    parameter2 = (ratio2 + 1.0) / ratio2

    p4 = (p10[0] + (p11[0] - p10[0]) * parameter1,
          p10[1] + (p11[1] - p10[1]) * parameter1)

    p5 = (p23[0] + (p22[0] - p23[0]) * parameter2,
          p23[1] + (p22[1] - p23[1]) * parameter2)

    return (p10[0], p10[1],
            p4[0], p4[1],
            p5[0], p5[1],
            p23[0], p23[1])

def tangential(c, dx, dy):
    """
    Find parameter(s) where a curve c is tangential to the vector (dx, dy)
    """
    assert len(c)==8

    x = numpy.mat(c[0::2]).transpose()
    qx = dy * DB * x
    y = numpy.mat(c[1::2]).transpose()
    qy = dx * DB * y

    valid = lambda x: (x>=0 and x<=1)

    return filter(valid, numpy.roots(map(float,qx-qy)))

def tangentRanges(c):
    """
    Return maximal and minimal x and y derivatives along the spline parameter
    """

    x = numpy.mat(c[0::2]).transpose()
    qx = DDB * x
    y = numpy.mat(c[1::2]).transpose()
    qy = DDB * y

    if qx[0]!=0:
        exx = - float(qx[1]) / qx[0]
    else:
        exx = -1

    if qy[0]!=0:
        exy = - float(qy[1]) / qy[0]
    else:
        exy = -1

    (v0x, v0y)   = splineTangent(c, 0)
    (exxv, dummy) = splineTangent(c, exx)
    (dummy,exyv ) = splineTangent(c, exy)
    (v1x, v1y)   = splineTangent(c, 1)

    if (exx>=0 and exx<1):
        minx = min(exxv, v0x, v1x)
        maxx = max(exxv, v0x, v1x)
    else:
        minx = min(v0x, v1x)
        maxx = max(v0x, v1x)

    if (exy>=0 and exy<1):
        miny = min(exyv, v0y, v1y)
        maxy = max(exyv, v0y, v1y)
    else:
        miny = min(v0y, v1y)
        maxy = max(v0y, v1y)
    
    return (minx, maxx, miny, maxy)


def inRange(x0, y0, x1, y1, alpha, beta):
    """
    If any point of the rectangle (x0, y0), (x1, y1) is inside the area
    spanned by two lines with angles alpha and beta, respectively, return true.
    """
    angles = [math.atan2(y0, x0), math.atan2(y0, x1), 
              math.atan2(y1, x1), math.atan2(y1, x0)]

    if (max(angles) >= alpha and min(angles) < beta):
        return True

    return False

def findRotatingTangent(c, alpha, beta, parameter0 = 0, parameter1 = 1):
    """
    Find points that are tangential to a line of angle 
    (alpha * (1 - parameter)) + (beta * parameter)
    """
    (minx, maxx, miny, maxy) = tangentRanges(c)

    assert(parameter1 > parameter0)        

    if inRange(minx, miny, maxx, maxy, alpha, beta):
        if abs(parameter1 - parameter0)<1e-5:
            return [parameter0]
        [c1, c2] = splineSplit(c)
        half = (alpha + beta) * 0.5
        halfparameter = (parameter0 + parameter1) * 0.5
        A = findRotatingTangent(c1, alpha, half, parameter0, halfparameter)
        B = findRotatingTangent(c2, half, beta, halfparameter, parameter1)
        return A + B
    else:
        return []
        

def integral(c):
    """
    Integral under the square of a spline over [0,1]
    """
    a0 = c[0]
    a1 = c[1]
    a2 = c[2]
    a3 = c[3]
    P = [1 / 7.0 * a0 ** 2,
         1 / 3.0 * a0 * a1,
         2 / 5.0 * a0 * a3 + 1 / 5.0 * a1 ** 2,
         1 / 2.0 * a0 * a3 + 1 / 2.0 * a1 * a2,
         2 / 3.0 * a1 * a3 + 1 / 3.0 * a2 ** 2,
         a2 * a3,
         a3 ** 2]

    return numpy.polyval(P, 1)
