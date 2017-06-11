import math
from OpenGL.GL import *


class AbstractTransformation(object):
    def transform(self, time):
        if time < 0:
            return
        if time >= 1:
            t = 1
        else:
            t = -0.5 * math.cos(math.pi * time) + 0.5

        self.raw_transform(t)

    def raw_transform(self, t):
        raise NotImplementedError()


class Translation(AbstractTransformation):
    def __init__(self, dx, dy, dz=0):
        self._dx = dx
        self._dy = dy
        self._dz = dz

    def raw_transform(self, t):
        glTranslate(t * self._dx, t * self._dy, t * self._dz)


class Rotation(AbstractTransformation):
    def __init__(self, angle, ax, ay, az):
        self._angle = angle
        self._ax = ax
        self._ay = ay
        self._az = az

    def raw_transform(self, t):
        glRotate(t * self._angle, self._ax, self._ay, t * self._az)


class Scale(AbstractTransformation):
    def __init__(self, sx, sy=None, sz=None):
        if sy is None:
            sy = sx
        if sz is None:
            sz = sy

        self._sx = sx
        self._sy = sy
        self._sz = sz

    def raw_transform(self, t):
        glScale(t * self._sx, t * self._sy, t * self._sz)


class TransformationSequence(object):
    coordinates = None
    transformations = None

    def transform(self, time):
        pass
