
import pyx

def capButt(p1, p2):
    
    (x1,y1) = p1.atend()
    (x2,y2) = p2.atend()

    (x3,y3) = p1.atbegin()
    (x4,y4) = p2.atbegin()
    
    cappedPath = p1 << pyx.path.line(x1,y1,x2,y2) << p2.reversed() << \
        pyx.path.line(x4,y4,x3,y3)
    
    return cappedPath
