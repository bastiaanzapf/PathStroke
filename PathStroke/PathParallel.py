
from pyx import *
from Vector import *

import CurveParallel
import Join


def joinOrSplit(p1, p2, joinType, dist, x, y):
    """
    cut p1 and p2 or append a join segment    
    either intersect or add a join about (x, y) in distance dist
    returns [p1_, p2_, join]
    """

    joinSegment = None

    a = p1.intersect(p2)

    if (len(a[0]) > 0):

        s1 = p1.split(a[0])
        s2 = p2.split(a[1])

        if len(a[0]) == 1:

            p1 = s1[0]
            p2 = s2[1]

        else:

            raise Exception("More than one intersection point")

    else:

        joinSegment = Join.joinPaths(joinType,
                                     p1,
                                     p2,
                                     x, y, dist)

    return [p1, p2, joinSegment]


def mergeCurves(curves):
    """
    Merge several curve segments
    """
    p = path.curve(*curves[0])

    for a in curves[1:]:

        c = path.curve(*a)

        s = p.intersect(c)

        if (len(s[0]) > 0):
            ps = p.split(s[0][0])
            cs = c.split(s[1][0])

            p = ps[0] << cs[1]
        else:
            p = p << c

    return p


def pathParallel(skeleton, dist=10, joinType='bevel', debug=None):

    strokes = []

    parallel = path.path()

    lastPoint = None
    previousParallelSegment = None

    close = False

    for apathitem in skeleton:

        if isinstance(apathitem, path.moveto):

            lastPoint = (apathitem.x_pt, apathitem.y_pt)
            currentPoint = lastPoint

            continue

        elif isinstance(apathitem, path.lineto):

            lastPoint = currentPoint
            currentPoint = (apathitem.x_pt, apathitem.y_pt)

            normal = dist * \
                (Vector(*lastPoint) - Vector(*currentPoint)) \
                .normalize().rot90deg()

            x0 = (Vector(*lastPoint) + normal)
            x1 = (Vector(*currentPoint) + normal)

            parallelSegment = path.line(x0.x[0], x0.x[1],
                                        x1.x[0], x1.x[1])

        elif isinstance(apathitem, path.curveto):

            lastPoint = currentPoint
            currentPoint = (apathitem.x3_pt, apathitem.y3_pt)

            curves = CurveParallel.curveParallel(
                [lastPoint[0], lastPoint[1],
                 apathitem.x1_pt, apathitem.y1_pt,
                 apathitem.x2_pt, apathitem.y2_pt,
                 apathitem.x3_pt, apathitem.y3_pt], dist, 0)

            parallelSegment = mergeCurves(curves)

        elif isinstance(apathitem, path.closepath):

            close = True

            parallelSegment = None

        else:
            raise Exception('''Can't handle path item %s''' % repr(apathitem))

        if not(parallelSegment is None):

            (x, y) = (unit.topt(lastPoint[0]),
                      unit.topt(lastPoint[1]))

            if not(previousParallelSegment is None):

                [previousParallelSegment, parallelSegment, joinSegment] \
                    = joinOrSplit(previousParallelSegment,
                                  parallelSegment,
                                  joinType, dist, x, y)

                if not(joinSegment is None):
                    parallelSegment = joinSegment << parallelSegment

                if len(parallel) > 0:
                    parallel = parallel << previousParallelSegment
                else:
                    parallel = previousParallelSegment

            previousParallelSegment = parallelSegment

        if close:

            # this is a different situation than above:
            # an intersection point must be a true self-intersection
            # of a closed path, not two parallel segments intersecting

            s = parallel.intersect(previousParallelSegment)

            # the second condition is necessary for spurious intersections
            # at the start of a parallel segment

            if (len(s[0]) == 0) | (s[1][0].normsubpathparam < 1e-5):

                parallel = parallel << previousParallelSegment

                (x, y) = (unit.topt(currentPoint[0]),
                          unit.topt(currentPoint[1]))

                joinSegment = Join.joinPaths(joinType,
                                             parallel,
                                             parallel,
                                             x, y, dist)

                parallel = parallel << joinSegment
                parallel.append(path.closepath())

            else:
                assert len(s[0]) == 1
                parallel = parallel.split(s[0])[1]
                previousParallelSegment = previousParallelSegment.split(
                    s[1])[0]

                parallel = parallel << previousParallelSegment
                parallel.append(path.closepath())

    return parallel
