
import math


class Vector:
    x = None

    def __init__(self, x, y):
        self.x = [x, y]

    def rot90deg(self):
        assert len(self.x) == 2
        return Vector(self.x[1], -self.x[0])

    def normalize(self):
        assert len(self.x) == 2
        f = math.sqrt(self.x[0]**2 + self.x[1]**2)
        return Vector(self.x[0] / f, self.x[1] / f)

    def __rmul__(self, f):
        assert isinstance(f, (float, int))
        return Vector(self.x[0] * f, self.x[1] * f)

    def __sub__(self, f):
        assert len(self.x) == len(f.x)
        assert len(self.x) == 2
        return Vector(self.x[0] - f.x[0],
                      self.x[1] - f.x[1])

    def __add__(self, f):
        assert len(self.x) == len(f.x)
        assert len(self.x) == 2
        return Vector(self.x[0] + f.x[0],
                      self.x[1] + f.x[1])

    def __str__(self):
        return "Vector (%f,%f)" % (self.x[0], self.x[1])
