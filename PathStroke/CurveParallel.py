
from pyx import *

# some rather involved code

# below: pyx

from numpy import *
from numpy.linalg import *
import Splines
from Util import *

B0=array([-1,3,-3,1])
B1=array([3,-6,3,0])
B2=array([-3,3,0,0])
B3=array([1,0,0,0])

DB0=array([-3,6,-3])
DB1=array([9,-12,3])
DB2=array([-9,6,0])
DB3=array([3,0,0])

DDB0=array([-6,6])
DDB1=array([18,-12])
DDB2=array([-18,6])
DDB3=array([6,0])

DDDB0=-6
DDDB1=18
DDDB2=-18
DDDB3=6

def splinePoint(c,at):

    x=polyval(B0,at)*c[0]+polyval(B1,at)*c[2]+ \
        polyval(B2,at)*c[4]+polyval(B3,at)*c[6]
    
    y=polyval(B0,at)*c[1]+polyval(B1,at)*c[3]+ \
        polyval(B2,at)*c[5]+polyval(B3,at)*c[7]

    return (x,y)

def splineTangent(c,at):

    dx=polyval(DB0,at)*c[0]+polyval(DB1,at)*c[2]+ \
        polyval(DB2,at)*c[4]+polyval(DB3,at)*c[6]
    
    dy=polyval(DB0,at)*c[1]+polyval(DB1,at)*c[3]+ \
        polyval(DB2,at)*c[5]+polyval(DB3,at)*c[7]

    return (dx,dy)

def parallelPoint(c,at,dist):
    assert len(c)==8
    assert isinstance(dist,(int,float))

    (x,y)=splinePoint(c,at)

    (dx,dy)=splineTangent(c,at)

    if (dx**2+dy**2!=0):
        f = 1/math.sqrt(dx**2+dy**2)
    else:
        f = 0

    normal = (-dy*f,dx*f)    

    return (x+dist*normal[0],y+dist*normal[1])


def checkParallel(curve,parallel,dist):
    """
    Measure an error between a curve and a proposed parallel
    """

    assert len(curve)==8
    assert len(parallel)==8
    error=0
    for i in [1,3,5,7]:
        a=i/8.0
        p1=splinePoint(curve,a)
        p2=splinePoint(parallel,a)
        weight=pyxLen(splineTangent(parallel,a))/8.0
        error+=(pyxLen(pyxSub(p1,p2))-dist)**2*weight

    return error

def curveParallel(c,dist,depth,dx0=None,dy0=None):
    """
    Construct a curve parallel in a given distance to a cubic bezier segment.
    
    c         curve segment (list of 8 float)
    dist      distance
    depth     recursion depth
    (dx0,dy0) suggested tangent to p0

    returns a list of curve segments
    """

    assert len(c)==8
    assert isinstance(c[0],float)

    (x_0,y_0)=parallelPoint(c,0  ,dist)
    (x_1,y_1)=parallelPoint(c,0.5,dist)
    (x_2,y_2)=parallelPoint(c,1  ,dist)

    if (dx0==None):
        (dx0,dy0)=splineTangent(c,0)

    (dx1,dy1)=splineTangent(c,0.5)

    # Proposal: tangent given in p0 and p1

    proposal = Splines.directedSpline2(x_0,y_0,x_1,y_1,x_2,y_2,
                                           dx0,dy0,dx1,dy1)

    if depth>5: # 4
        return [proposal]

    error = checkParallel(c, proposal, abs(dist))

    if (error<0.05): # 0.01
        return [proposal]

    # split at 1/2, 1/3 or 1/5

    parts1 = Splines.splineSplit(c,1/2.0)

    p11=curveParallel(parts1[0],dist,depth+1)
    p12=curveParallel(parts1[1],dist,depth+1)

    if (depth<4):

        parts2 = Splines.splineSplit(c,1/3.0)
        
        p21=curveParallel(parts2[0],dist,depth+1)
        p22=curveParallel(parts2[1],dist,depth+1)
        
        if (len(p11)+len(p12) > len(p21)+len(p22)):
            return p21 + p22

        parts3 = Splines.splineSplit(c,1/5.0)
        
        p31=curveParallel(parts3[0],dist,depth+1)
        p32=curveParallel(parts3[1],dist,depth+1)

        if (len(p11)+len(p12) > len(p31)+len(p32)):
            return p31 + p32

    return p11 + p12

