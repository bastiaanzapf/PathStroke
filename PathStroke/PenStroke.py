
# Pen Strokes (similar to MetaFont "penstroke")
#
# stroke a path with a linear ("calligraphy") pen 
#
# this is slightly different to circular brush strokes since a line 
# can be continued by the opposite edge of the pen. 
#
# angles must be a list with as many entries as there are points in the 
# curve

import Splines
import pyx 
import math
import CurveParallel
import PathParallel

def distAngle(x, y, dist, angle):
    return (x + dist * math.cos(angle),
            y + dist * math.sin(angle))

def penStroke(skeleton, angles, dist=10):

    posParallel = pyx.path.path()
    negParallel = pyx.path.path()

    lastPoint = None
    posPreviousParallelSegment = None
    negPreviousParallelSegment = None

    close = False

    for apathitem in skeleton:

        assert not(close)

        if isinstance(apathitem, pyx.path.moveto):

            lastPoint = (apathitem.x_pt, apathitem.y_pt)
            currentPoint = lastPoint

            lastAngle = angles.pop()

            continue

        elif isinstance(apathitem, pyx.path.lineto):

            lastPoint = currentPoint
            currentPoint = (apathitem.x_pt, apathitem.y_pt)        

            (x0, y0) = distAngle(currentPoint[0], currentPoint[1],
                                   dist, lastAngle)
            (x1, y1) = distAngle(currentPoint[0], currentPoint[1],
                                 - dist, lastAngle)

            lastAngle = angles.pop()

            (x2, y2) = distAngle(currentPoint[0], currentPoint[1],
                                   dist, lastAngle)
            (x3, y3) = distAngle(currentPoint[0], currentPoint[1],
                                 - dist, lastAngle)

            posParallelSegment = pyx.path.line(x0, y0, x1, y1)
            negParallelSegment = pyx.path.line(x2, y2, x3, y3)
            
        elif isinstance(apathitem, pyx.path.curveto):

            lastPoint = currentPoint
            currentPoint = (apathitem.x3_pt, apathitem.y3_pt)

            thisAngle = angles.pop()

            posCurves = CurveParallel.penParallel(
                [lastPoint[0], lastPoint[1],
                 apathitem.x1_pt, apathitem.y1_pt,
                 apathitem.x2_pt, apathitem.y2_pt,
                 apathitem.x3_pt, apathitem.y3_pt], 
                lastAngle, thisAngle,                
                dist, 0)

            negCurves = CurveParallel.penParallel(
                [lastPoint[0], lastPoint[1],
                 apathitem.x1_pt, apathitem.y1_pt,
                 apathitem.x2_pt, apathitem.y2_pt,
                 apathitem.x3_pt, apathitem.y3_pt],
                lastAngle, thisAngle,                
                -dist, 0)

            lastAngle = thisAngle

            posParallelSegment = PathParallel.mergeCurves(posCurves)
            negParallelSegment = PathParallel.mergeCurves(negCurves)

        elif isinstance(apathitem, pyx.path.closepath):

            close = True

            posParallelSegment = None
            negParallelSegment = None

        else:
            raise Exception('''Can't handle path item %s''' % repr(apathitem))

        if not(posParallelSegment is None):

            if len(posParallel) > 0:
                posParallel = posParallel << posParallelSegment
                negParallel = negParallel << negParallelSegment
            else:
                posParallel = posParallelSegment
                negParallel = negParallelSegment

    return (posParallel, negParallel)

