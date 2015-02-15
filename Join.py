
from pyx import *
import math
import Splines

def roundJoin(p1,p2,x,y,dx1,dy1,dx2,dy2,dist,debug):

    CircleConstant = 3.0/4*(math.sqrt(2)-1)

    assert isinstance(p1,tuple)
    assert isinstance(p2,tuple)

    (x0,y0) = p1
    (x3,y3) = p2

    (dx0,dy0)=(x-x0,y-y0)
    (dx3,dy3)=(x-x3,y-y3)

    alpha = math.atan2(dy0,dx0)
    delta = math.atan2(dy3,dx3)

    angle = delta-alpha

    if (abs(angle) < math.pi/2):

        f = math.sin(alpha-delta)

        (x1,y1) = (x0+math.sin(alpha)*f*dist*CircleConstant,
                   y0-math.cos(alpha)*f*dist*CircleConstant)
        
        (x2,y2) = (x3-math.sin(delta)*f*dist*CircleConstant,
                   y3+math.cos(delta)*f*dist*CircleConstant)

        return path.curve(x0,y0,x1,y1,x2,y2,x3,y3)

    else:

        beta = (alpha+delta)*0.5

        (xs,ys) = (x-math.cos(beta)*abs(dist),
                   y-math.sin(beta)*abs(dist))
        
        (dxs,dys) = ( -math.sin(beta),
                       math.cos(beta))

        (dx0,dy0) = (dx1-x0,dy1-y0)
        (dx3,dy3) = (x3-dx2,y3-dy2)

        assert abs(math.sqrt(dx0**2+dy0**2)-1)<1e-5
        assert abs(math.sqrt(dx3**2+dy3**2)-1)<1e-5

        f = CircleConstant*abs(dist)*math.sin((alpha-delta)*0.5)

        a = 1.0/math.sqrt(2)

        (x,y) = (x0+(xs-x0)*(1-a),y0+(ys-y0)*(a))

        A = Splines.directedSpline([(x0,y0),(x,y),(xs,ys)],
                                       dx0,dy0,dxs,dys,0,0)

        (x,y) = (x3+(xs-x3)*(1-a),y3+(ys-y3)*(a))

        B = Splines.directedSpline([(xs,ys),(x,y),(x3,y3)],
                                       dxs,dys,dx3,dy3,0,0)

        c1 = path.curve(*A)
        c2 = path.curve(*B)

        return c1 << c2

def hollowJoin(p1,p2,x,y,dist):
    (x0,y0)=p1.atend()
    (x3,y3)=p2.atbegin()
    
    (x0,y0)=(unit.topt(x0),unit.topt(y0))
    (x3,y3)=(unit.topt(x3),unit.topt(y3))

    (dx0,dy0)=(x0-x,y0-y)
    (dx3,dy3)=(x3-x,y3-y)

    mangle = ((x0+x3)*0.5,(y0+y3)*0.5)

    alpha = math.atan2(dy0,dx0)
    delta = math.atan2(dy3,dx3)

    beta = (alpha*2.0+delta)/3.0
    gamma = (alpha+delta*2.0)/3.0

    if alpha<delta:
        dist = -dist
            
    (x1,y1) = (mangle[0] - math.cos(gamma)*dist, 
               mangle[1] - math.sin(gamma)*dist)
    (x2,y2) = (mangle[0] - math.cos(beta )*dist, 
               mangle[1] - math.sin(beta )*dist)

    return path.curve(
        *Splines.naturalSpline([(x0,y0),(x1,y1),(x2,y2),(x3,y3)])
        )

def miterJoin(p1,p2,dist):
    """
    Extend tangents of two paths for a certain distance, cut them in the 
    intersection point. p1 is pointing outwards, p2 inwards.
    """

    t1=p1.tangent(p1.end(),dist)
    t2=p2.tangent(p2.begin(),-dist)
        
    intersections=t1.intersect(t2)

    if (len(intersections[0])>0):

        segment1 = t1.split(intersections[0])[0]
        segment2 = t2.split(intersections[1])[0]
        segment = segment1.joined(segment2.reversed())
        return segment

    else:
        return t1.joined(t2.reversed())

def joinPaths(joinType,p1,p2,dx1,dy1,dx2,dy2,x,y,dist,debug):
    if (joinType=='bevel'):

        (x0,y0)=p1.atend()
        (x1,y1)=p2.atbegin()
        return path.line(x0,y0,x1,y1)

    if (joinType=='miter'):

        return miterJoin(p1,p2,abs(dist*0.5))

    if (joinType=='round'):

        return roundJoin(p1,p2,x,y,dx1,dy1,dx2,dy2,dist,debug)

    if (joinType=='hollow'):

        return hollowJoin(p1,p2,x,y,dist)
