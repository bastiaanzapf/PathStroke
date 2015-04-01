
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

def append(posParallel, negParallel, pos, neg):
    """
    append segments of a pen stroke
    """

    if (len(posParallel) == 0):

        return (pos, neg)

    else:
        a= posParallel.intersect(neg)
        b= negParallel.intersect(pos)
        c= posParallel.intersect(pos)
        d= negParallel.intersect(neg)

        if len(a[0]) != 0:
            s = neg.split(a[1])
            t = posParallel.split(a[0])
            posParallel = t[0] << s[1]

            negParallel = negParallel << pos
        elif len(b[0]) != 0:
            s = pos.split(b[1])
            t = negParallel.split(b[0])
            negParallel = t[0] << s[1]

            posParallel = posParallel << neg

        elif len(c[0]) != 0:

            s = pos.split(c[1])
            t = posParallel.split(c[0])
            posParallel = t[0] << s[1]

            negParallel = negParallel << neg
            
        c = pos.intersect(neg)

        return (posParallel, negParallel)

def penStroke(skeleton, angles, dist=10):
    """
    stroke a pyx path "skeleton" with a linear pen of radius dist 
    held in angles "angles"
    """
    posParallel = pyx.path.path()
    negParallel = pyx.path.path()

    lastPoint = None
    posPreviousParallelSegment = None
    negPreviousParallelSegment = None

    close = False

    i = 0

    for apathitem in skeleton:

        thisAngle = angles[i]
        i = i + 1
        assert not(close)

        if isinstance(apathitem, pyx.path.moveto) or \
                isinstance(apathitem, pyx.path.moveto_pt):
        

            lastPoint = (apathitem.x_pt, apathitem.y_pt)
            currentPoint = lastPoint

            lastAngle = thisAngle

            continue

        elif isinstance(apathitem, pyx.path.lineto) or \
            isinstance(apathitem, pyx.path.lineto_pt):

            lastPoint = currentPoint
            currentPoint = (apathitem.x_pt, apathitem.y_pt)        

            (x0, y0) = distAngle(currentPoint[0], currentPoint[1],
                                   dist, lastAngle)
            (x1, y1) = distAngle(currentPoint[0], currentPoint[1],
                                 - dist, lastAngle)

            lastAngle = thisAngle

            (x2, y2) = distAngle(currentPoint[0], currentPoint[1],
                                   dist, lastAngle)
            (x3, y3) = distAngle(currentPoint[0], currentPoint[1],
                                 - dist, lastAngle)

            pos = pyx.path.line(x0, y0, x1, y1)
            neg = pyx.path.line(x2, y2, x3, y3)            

            (posParallel, negParallel) = append(posParallel, negParallel, 
                                                pos, neg)
            
            print "Muh %s %s" % (posParallel, negParallel)

        elif isinstance(apathitem, pyx.path.curveto) or \
            isinstance(apathitem, pyx.path.curveto_pt):

            lastPoint = currentPoint
            currentPoint = (apathitem.x3_pt, apathitem.y3_pt)

            c=[lastPoint[0], lastPoint[1],
               apathitem.x1_pt, apathitem.y1_pt,
               apathitem.x2_pt, apathitem.y2_pt,
               apathitem.x3_pt, apathitem.y3_pt]

            pos = CurveParallel.penParallel(c, dist,
                                            lastAngle, thisAngle, 0)

            neg = CurveParallel.penParallel(c, -dist,
                                            lastAngle, thisAngle, 0)

            minAngle = min(lastAngle, thisAngle)
            maxAngle = max(lastAngle, thisAngle) + 1e-5
        
            a = Splines.findRotatingTangent(pos[0], minAngle, maxAngle)
            b = Splines.findRotatingTangent(neg[0], minAngle, maxAngle)

            if len(a) != 0:
                
                flip = False
                
                posSegments = Splines.splineMultipleSplit(pos[0],a)
                negSegments = Splines.splineMultipleSplit(neg[0],b)

                for (ps,ns) in zip(posSegments,negSegments):

                    p_ = pyx.path.curve(*ps)
                    n_ = pyx.path.curve(*ns)

                    if (flip):
                        (posParallel, negParallel) = \
                            append(posParallel, negParallel, n_, p_)
                    else:
                        (posParallel, negParallel) = \
                            append(posParallel, negParallel, p_, n_)

                    flip = True

            else:
                pos = pyx.path.curve(*pos[0])
                neg = pyx.path.curve(*neg[0])

                (posParallel, negParallel) = \
                    append(posParallel, negParallel, pos, neg)

            lastAngle = thisAngle
            
        elif isinstance(apathitem, pyx.path.closepath):

            close = True

        else:
            raise Exception('''Can't handle path item %s''' % repr(apathitem))

    return (posParallel, negParallel)

