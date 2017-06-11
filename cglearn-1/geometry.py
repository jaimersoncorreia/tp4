import os
import re

from OpenGL.GL import *


class AbstractPrimitive(object):
    def __init__(self, geometry, *args, **kwargs):
        self.material_name = kwargs.pop('material_name', None)

        self._vertex_indexes = []
        self._material_indexes = []
        self._normal_indexes = []
        self._geometry = geometry

        for arg in args:
            m = re.match(r'(\d+)(?:/(\d*)(?:/(\d*)?))?$', arg)
            vertex_index = int(m.group(1)) - 1
            if m.group(2):
                material_index = int(m.group(2)) - 1
            else:
                material_index = None
            if m.group(3):
                normal_index = int(m.group(3)) - 1
            else:
                normal_index = None

            self._vertex_indexes.append(vertex_index)
            self._material_indexes.append(material_index)
            self._normal_indexes.append(normal_index)

    def set_material(self, opacity=1.0):
        diffuse_color = [0.9, 0.7, 0.4]
        if self.material_name:
            material = self._geometry._materials[self.material_name]
            if 'Kd' in material:
                diffuse_color = list(material['Kd'])

        if len(diffuse_color) == 3:
            diffuse_color.append(opacity)
        else:
            diffuse_color[3] *= opacity

        glColor(*diffuse_color)

    def get_vertexes(self):
        raise NotImplementedError()

    def fill(self, opacity=1.0):
        raise NotImplementedError()

    def draw_wireframe(self, opacity=1.0):
        raise NotImplementedError()


class Triangle(AbstractPrimitive):
    def get_vertexes(self):
        return [self._geometry._vertexes[index]
                for index in self._vertex_indexes]

    def fill(self, opacity=1.0):
        self.set_material(opacity=opacity)
        glBegin(GL_TRIANGLES)
        for point_index, material_index, normal_index in zip(
                self._vertex_indexes, self._material_indexes,
                self._normal_indexes):
            if material_index:
                pass # @TODO
            if normal_index:
                glNormal(*self._geometry._normals[normal_index])
            glVertex(*self._geometry._vertexes[point_index])
        glEnd()

    def draw_wireframe(self, opacity=1.0):
        glBegin(GL_LINE_LOOP)
        for index in self._vertex_indexes:
            glVertex(*self._geometry._vertexes[index])
        glEnd()


class Quadrangle(AbstractPrimitive):
    def get_vertexes(self):
        return [self._geometry._vertexes[index]
                for index in self._vertex_indexes]

    def fill(self, opacity=1.0):
        self.set_material(opacity=opacity)
        glBegin(GL_QUADS)
        for point_index, material_index, normal_index in zip(
                self._vertex_indexes, self._material_indexes,
                self._normal_indexes):
            if material_index:
                pass # @TODO
            if normal_index:
                glNormal(*self._geometry._normals[normal_index])
            glVertex(*self._geometry._vertexes[point_index])
        glEnd()

    def draw_wireframe(self, opacity=1.0):
        glBegin(GL_LINE_LOOP)
        for index in self._vertex_indexes:
            glVertex(*self._geometry._vertexes[index])
        glEnd()


class Line(AbstractPrimitive):
    def get_vertexes(self):
        return [self._geometry._vertexes[index]
                for index in self._vertex_indexes]

    def fill(self, opacity=1.0):
        pass

    def draw_wireframe(self, opacity=1.0):
        glBegin(GL_LINES)
        for point_index, material_index, normal_index in zip(
                self._vertex_indexes, self._material_indexes,
                self._normal_indexes):
            if material_index:
                pass # @TODO
            if normal_index:
                glNormal(*self._geometry._normals[normal_index])
            glVertex(*self._geometry._vertexes[point_index])
        glEnd()


class Geometry(object):
    _vertexes = []
    _normals = []
    _objects = {}

    def read_mtl(self, filepath):
        fh = open(filepath)
        material_data = {}

        for line in fh:
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            parts = line.split(' ')
            command = parts[0]
            args = parts[1:]

            if command == 'newmtl':
                material_name = args[0]
                material_data = {}
                self._materials[material_name] = material_data

            elif command in ('Ka', 'Kd', 'Ks', 'd'):
                material_data[command] = list(map(float, args))

            elif command == 'Tr':
                material_data['d'] = 1.0 - float(args[0])

    def read_obj(self, filepath):
        self._vertexes = []
        self._normals = []
        self._materials = {}
        self._objects = {}

        fh = open(filepath)
        current_material_name = None
        current_object_name = None

        def add_primitive(primitive):
            self._objects.setdefault(current_object_name, []).append(primitive)

        for line in fh:
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            parts = line.split(' ')
            command = parts[0]
            args = parts[1:]

            if command == 'o':
                current_object_name = args[0]

            elif command == 'mtllib':
                self.read_mtl(os.path.join(os.path.dirname(filepath), args[0]))

            elif command == 'usemtl':
                current_material_name = args[0]

            elif command == 'v':
                self._vertexes.append(
                    (float(args[0]), float(args[1]), float(args[2])))

            elif command == 'vn':
                self._normals.append(
                    (float(args[0]), float(args[1]), float(args[2])))

            elif command == 'l':
                if len(args) == 2:
                    add_primitive(Line(
                        self, material_name=current_material_name, *args))
                else:
                    raise ValueError('Invalid number of parameters.')

            elif command == 'f':
                if len(args) == 3:
                    add_primitive(Triangle(
                        self, material_name=current_material_name, *args))
                elif len(args) == 4:
                    add_primitive(Quadrangle(
                        self, material_name=current_material_name, *args))
                else:
                    raise ValueError('Invalid number of parameters.')

    @property
    def object_names(self):
        return list(self._objects.keys())

    def fill(self, object_name, *args, **kwargs):
        for primitive in self._objects[object_name]:
            primitive.fill(*args, **kwargs)

    def draw_wireframe(self, object_name):
        for primitive in self._objects[object_name]:
            primitive.draw_wireframe()

    def get_vertexes(self, object_name):
        vertexes = set()
        for primitive in self._objects[object_name]:
            vertexes.update(primitive.get_vertexes())
        return list(vertexes)

    def get_bounds(self, objects=None):
        if objects is None:
            objects = self.object_names

        vertexes = set()

        bounds_min = (0.0, 0.0, 0.0)
        bounds_max = (0.0, 0.0, 0.0)

        for object_name in objects:
            object = self._objects[object_name]
            for primitive in object:
                vertexes.update(primitive.get_vertexes())

        for vertex in vertexes:
            if bounds_min is None:
                bounds_min = vertex
                bounds_max = vertex
            else:
                bounds_min = list(map(min, zip(bounds_min, vertex)))
                bounds_max = list(map(max, zip(bounds_max, vertex)))

        if bounds_min is None:
            return (-1.0, -1.0, -1.0), (1.0, 1.0, 1.0)

        for index in range(len(bounds_min)):
            if bounds_min[index] == bounds_max[index]:
                bounds_min = list(bounds_min)
                bounds_max = list(bounds_max)
                bounds_min[index] -= 0.5
                bounds_max[index] += 0.5

        return tuple(bounds_min), tuple(bounds_max)
