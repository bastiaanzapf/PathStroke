
from pyx import *
from Vector import *

import CurveParallel
import Join

def pathParallel(skeleton,dist=10,joinType='bevel',debug=None):

    strokes=[]

    parallel=path.path()
    
    lastPoint=None

    for apathitem in skeleton:

        if isinstance (apathitem, path.moveto):

            lastPoint = (apathitem.x_pt,apathitem.y_pt)
            currentPoint = lastPoint

            continue

        elif isinstance (apathitem, path.lineto):

            lastPoint = currentPoint
            currentPoint = (apathitem.x_pt,apathitem.y_pt)

            normal = dist * \
                (Vector(*lastPoint) - Vector(*currentPoint)) \
                .normalize().rot90deg()

            x0 = (Vector(*lastPoint) + normal)
            x1 = (Vector(*currentPoint) + normal)

            parallelSegment = path.line(x0.x[0],x0.x[1],
                                        x1.x[0],x1.x[1])

        elif isinstance (apathitem, path.curveto):
                        
            lastPoint = currentPoint
            currentPoint = (apathitem.x3_pt,apathitem.y3_pt)

            curves = CurveParallel.curveParallel(
                [lastPoint[0], lastPoint[1],
                 apathitem.x1_pt,apathitem.y1_pt,
                 apathitem.x2_pt,apathitem.y2_pt,
                 apathitem.x3_pt,apathitem.y3_pt]
                ,dist,0)

            parallelSegment = path.curve(*curves[0])

            for a in curves[1:]:

                c = path.curve(*a)
                path.set(1e-10)
                s = parallelSegment.intersect(c)

                if (len(s[0])>0):
                    ps = parallelSegment.split(s[0][0])
                    cs = c.split(s[1][0])

                    parallelSegment = ps[0] << cs[1]
                else:
                    parallelSegment = parallelSegment << c
                path.set(1e-5)

        elif isinstance (apathitem, path.closepath):

            pass

        else:
            raise Exception("Can't handle path item %s" % repr(apathitem))

        assert(parallelSegment)

        if (len(parallel)>0):

            path.set(1e-10)

            a = parallel.intersect(parallelSegment)

            path.set(1e-5)

#            debug.stroke(parallelSegment,[color.rgb(1,0,0),
#                                          style.linewidth.THICK])

            if (len(a[0])>0):
                parallelSegment = parallelSegment.split(a[1])[-1]
                parallel = parallel.split(a[0])[0]
            else:

                (x,y)=(unit.topt(lastPoint[0]),unit.topt(lastPoint[1]))

                p0 = parallel.atend()
                (x0,y0)=(unit.topt(p0[0]),unit.topt(p0[1]))

                p1 = parallelSegment.atbegin()
                (x1,y1)=(unit.topt(p1[0]),unit.topt(p1[1]))

                t0 = parallel.tangent(parallel.end(),1)[0][0]

                t1 = parallelSegment.tangent(parallelSegment.begin(),1)[0][0]

                (t0x,t0y)=(unit.topt(t0.x1_pt),unit.topt(t0.y1_pt))
                (t1x,t1y)=(unit.topt(t1.x1_pt),unit.topt(t1.y1_pt))

                joinSegment = Join.joinPaths(joinType,
                                             (x0,y0),
                                             (x1,y1),
                                             t0x,t0y,t1x,t1y,
                                             x,y,dist,debug)
                parallel = parallel.joined(joinSegment)

                path.set(1e-10)
                a = parallel.intersect(parallelSegment)
                path.set(1e-5)

                if (len(a[0])>0):
                    parallelSegment = parallelSegment.split(a[1][0])[1]
                    parallel = parallel.split(a[0][0])[0]

            parallel = parallel.joined(parallelSegment)

        else:
            parallel = parallelSegment


    return parallel
