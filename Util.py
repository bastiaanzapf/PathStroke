
import math
from pyx import *

def pyxAdd(a,b):
    return (a[0]+b[0],a[1]+b[1])

def pyxSub(a,b):
    return (a[0]-b[0],a[1]-b[1])

def pyxMul(a,f):
    return (a[0]*f,a[1]*f)

def pyxLen(a):
    assert(len(a)==2)    
    return math.sqrt(unit.topt(a[0])**2+unit.topt(a[1])**2)

def pyxSplit(a,parameter=0.5):
    assert len(a)==2
    assert isinstance(a[0],path.moveto_pt)
    assert isinstance(a[1],path.curveto_pt)
    p0=(a[0].x_pt,a[0].y_pt)
    p1=(a[1].x1_pt,a[1].y1_pt)
    p2=(a[1].x2_pt,a[1].y2_pt)
    p3=(a[1].x3_pt,a[1].y3_pt)
    newcurves=path.path();
    newcurves.append(path.moveto(p0[0],p0[1]))
    p4=pyxAdd(p0,pyxMul(pyxSub(p1,p0),parameter))
    p5=pyxAdd(p1,pyxMul(pyxSub(p2,p1),parameter))
    p6=pyxAdd(p2,pyxMul(pyxSub(p3,p2),parameter))
    p7=pyxAdd(pyxMul(p4,1-parameter),pyxMul(p5,parameter))
    p8=pyxAdd(pyxMul(p5,1-parameter),pyxMul(p6,parameter))
    p9=pyxAdd(pyxMul(p7,1-parameter),pyxMul(p8,parameter))
    newcurves.append(path.curveto(p4[0],p4[1],
                                  p7[0],p7[1],
                                  p9[0],p9[1]))
    newcurves.append(path.curveto(p8[0],p8[1],
                                  p6[0],p6[1],
                                  p3[0],p3[1]))
    return newcurves
