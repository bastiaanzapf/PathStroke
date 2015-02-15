
#
# Some spline tricks. This is very chaotic.
#
# http://graphics.pixar.com/people/derose/publications/CubicClassification/paper.pdf

import operator
import math
import numpy

from Util import *

B=numpy.array([[-1,3,-3,1],[3,-6,3,0],[-3,3,0,0],[1,0,0,0]])

BD=numpy.array([[0,-3,6,-3],[0,9,-12,3],[0,-9,6,0],[0,3,0,0]])

BDD=numpy.array([[-6,6],[18,-12],[-18,6],[6,0]])

natSpline=numpy.array(numpy.zeros((4,4)))

for i in range(0,4):
    for j in range(0,4):
        natSpline[i][j]=numpy.polyval(B[j][:],i*1.0/3)

dirSpline=numpy.array(numpy.zeros((4,4)))

for i in range(0,3):
    for j in range(0,4):
        dirSpline[i][j]=numpy.polyval(B[j][:],i/2.0)

for j in range(0,4):
     dirSpline[3][j]=numpy.polyval(BD[j][:],0)

def naturalSpline(p):
    """
    Return control points of a "natural spline"
    """
    assert len(p)    == 4
    assert len(p[0]) == 2
    assert len(p[1]) == 2
    assert len(p[2]) == 2
    assert len(p[3]) == 2
                
    b1=numpy.array([p[0][0],p[1][0],p[2][0],p[3][0]])
    b2=numpy.array([p[0][1],p[1][1],p[2][1],p[3][1]])
 
    x=numpy.linalg.solve(natSpline,b1)
    y=numpy.linalg.solve(natSpline,b2)
 
    return (x[0],y[0],x[1],y[1],
            x[2],y[2],x[3],y[3])

C=numpy.matrix([[1,0,0,0],[.125,.375,.375,.125],[0,0,0,1],[-.75,-.75,.75,.75]])

D=numpy.matrix(numpy.zeros((8,8)))

for i in range(0,3):
    for j in range(0,4):
        bep = numpy.polyval(B[j][:],i/2.0)
        D[i  ,j  ]=bep
        D[i+4,j+4]=bep

def directedMatrix(a,b,c,d,e,f):
    
    A=D.copy()

    for j in range(0,4):
        bep = numpy.polyval(BD[j][:],0)
        A[3,j  ] =  b*bep
        A[3,j+4] = -a*bep
        bep = numpy.polyval(BD[j][:],1)
        A[7,j  ] =  d*bep
        A[7,j+4] = -c*bep

    for j in range(0,4):
        bep=numpy.polyval(BD[j][:],0.5)
        A[3,j  ] +=  f*bep*0.5
        A[3,j+4] += -e*bep*0.5

    for j in range(0,4):
        bep=numpy.polyval(BD[j][:],0.5)
        A[7,j  ] +=  f*bep*0.5
        A[7,j+4] += -e*bep*0.5

    return A

def directedMatrix2(a,b,c,d):
    
    A=D.copy()

    for j in range(0,4):
        bep = numpy.polyval(BD[j][:],0)
        A[3,j  ] =  b*bep
        A[3,j+4] = -a*bep
        bep = numpy.polyval(BD[j][:],0.5)
        A[7,j  ] =  d*bep
        A[7,j+4] = -c*bep

    return A

def directedMatrix4(a,b,c,d):
    
    A=D.copy()

    for j in range(0,4):
        bep = numpy.polyval(BD[j][:],0.25)
        A[3,j  ] =  b*bep
        A[3,j+4] = -a*bep
        bep = numpy.polyval(BD[j][:],0.75)
        A[7,j  ] =  d*bep
        A[7,j+4] = -c*bep

    return A

def directedSpline(p,a,b,c,d,e,f):

    """
    Return control points of a Spline through three points p, with 
    set tangents 
    in p0: (a,b)
    in p2: (c,d)
    """

    assert len(p)    == 3
    assert len(p[0]) == 2
    assert len(p[1]) == 2
    assert len(p[2]) == 2
    assert isinstance(a,float)
    assert isinstance(b,float)
    assert isinstance(c,float)
    assert isinstance(d,float)

    D=directedMatrix(a,b,c,d,e,f)

    assert isinstance(D,numpy.matrix)

    b=numpy.matrix([[p[0][0]],[p[1][0]],[p[2][0]],[0],
                    [p[0][1]],[p[1][1]],[p[2][1]],[0]])

    x=numpy.linalg.solve(D,b)

    return (float(p[0][0]),float(p[0][1]),
            float(x[1]),float(x[5]),
            float(x[2]),float(x[6]),
            float(p[2][0]),float(p[2][1]))

def directedSpline2(x0,y0,x1,y1,x2,y2,a,b,c,d):

    """
    Return control points of a Spline through three points (xn,yn), with 
    set tangents 
    in (x0,y0): (a,b)
    in (x1,y1): (c,d)
    """
    assert(isinstance(x0,float))
    assert(isinstance(y0,float))
    assert(isinstance(x1,float))
    assert(isinstance(y1,float))
    assert(isinstance(x2,float))
    assert(isinstance(y2,float))
    assert(isinstance(a,float))
    assert(isinstance(b,float))
    assert(isinstance(c,float))
    assert(isinstance(d,float))

    D=directedMatrix2(a,b,c,d)

    assert isinstance(D,numpy.matrix)

    v=numpy.matrix([[x0],[x1],[x2],[0],
                    [y0],[y1],[y2],[0]])

    x=numpy.linalg.solve(D,v)

    return (float(x0),float(y0),
            float(x[1]),float(x[5]),
            float(x[2]),float(x[6]),
            float(x2),float(y2))

def directedSpline3(p,a,b):

    """
    Return control points of a Spline through three points p, with 
    set first derivative
    in p0: (a,b)
    """

    assert len(p)    == 3
    assert len(p[0]) == 2
    assert len(p[1]) == 2
    assert len(p[2]) == 2
    assert isinstance(a,float)
    assert isinstance(b,float)
    assert isinstance(D,numpy.matrix)

    bx=numpy.matrix([[p[0][0]],[p[1][0]],[p[2][0]],[a]])
    
    by=numpy.matrix([[p[0][1]],[p[1][1]],[p[2][1]],[b]])

    x=numpy.linalg.solve(dirSpline,bx)
    y=numpy.linalg.solve(dirSpline,by)

    return (float(p[0][0]),float(p[0][1]),
            float(x[1]),float(y[1]),
            float(x[2]),float(y[2]),
            float(p[2][0]),float(p[2][1]))

def directedSpline4(x0,y0,x1,y1,x2,y2,a,b,c,d):

    """
    Return control points of a Spline through three points (xn,yn), with 
    set tangents 
    at parameter 0.25: (a,b)
    in (x2,y2): (c,d)
    """
    assert(isinstance(x0,float))
    assert(isinstance(y0,float))
    assert(isinstance(x1,float))
    assert(isinstance(y1,float))
    assert(isinstance(x2,float))
    assert(isinstance(y2,float))
    assert(isinstance(a,float))
    assert(isinstance(b,float))
    assert(isinstance(c,float))
    assert(isinstance(d,float))

    D=directedMatrix2(a,b,c,d)

    assert isinstance(D,numpy.matrix)

    v=numpy.matrix([[x0],[x1],[x2],[0],
                    [y0],[y1],[y2],[0]])

    x=numpy.linalg.solve(D,v)

    return (float(x0),float(y0),
            float(x[1]),float(x[5]),
            float(x[2]),float(x[6]),
            float(x2),float(y2))


def splineSplit(curve,parameter=0.5):
    assert len(curve)==8
    p0=(curve[0],curve[1])
    p1=(curve[2],curve[3])
    p2=(curve[4],curve[5])
    p3=(curve[6],curve[7])

    p4=pyxAdd(p0,pyxMul(pyxSub(p1,p0),parameter))
    p5=pyxAdd(p1,pyxMul(pyxSub(p2,p1),parameter))
    p6=pyxAdd(p2,pyxMul(pyxSub(p3,p2),parameter))
    p7=pyxAdd(pyxMul(p4,1-parameter),pyxMul(p5,parameter))
    p8=pyxAdd(pyxMul(p5,1-parameter),pyxMul(p6,parameter))
    p9=pyxAdd(pyxMul(p7,1-parameter),pyxMul(p8,parameter))

    newcurves=[[p0[0],p0[1],
                p4[0],p4[1],
                p7[0],p7[1],
                p9[0],p9[1]],
               [p9[0],p9[1],
                p8[0],p8[1],
                p6[0],p6[1],
                p3[0],p3[1]]];
                
    return newcurves

def suggestSplitParameters(curve):
    assert len(curve)==8

    result=[]

    a=0
    b=0
    for i in range(0,4):
        a=a+BDD[i][0]*curve[i*2]
        b=b+BDD[i][1]*curve[i*2]

    if (b/a > 0) & (b/a <1):
        result=[b/a]
    a=0
    b=0

    for i in range(0,4):
        a=a+BDD[i][0]*curve[i*2+1]
        b=b+BDD[i][1]*curve[i*2+1]

    if (b/a > 0) & (b/a < 1):
        result=result+[b/a]

    return result
