#!/usr/bin/env python3

import sys
import math
import argparse
import importlib

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

import numpy

from transformation import *
from geometry import *
from timing import Timing
import config
from context import Context
from drawingutils import *


parser = argparse.ArgumentParser()
parser.add_argument("configuration_filepath",
                    metavar="CONFIG_FILE", nargs='?',
                    help="JSON configuration file to load")
options = parser.parse_args()
config = config.load_config_file(options.configuration_filepath)


compor_cena = None
processar_teclado = None

try:
    student_module = importlib.import_module(config.module_name)
    compor_cena = getattr(student_module, config.callback_name)
    processar_teclado = getattr(student_module, "processar_teclado", None)
except ImportError:
    print("*** Atencao: Arquivo %s.py nao foi encontrado."
          % config.module_name, file=sys.stderr)
except AttributeError:
    print("*** Atencao: Arquivo %s.py nao possui funcao '%s'."
          % (config.module_name, config.callback_name), file=sys.stderr)

if compor_cena is None:
    def compor_cena(context):
        for object_name in context.object_names:
            context.draw(object_name)

if processar_teclado is None:
    def processar_teclado(key):
        pass


glutInit(sys.argv)
glutInitDisplayMode(GLUT_RGB | GLUT_DOUBLE | GLUT_DEPTH)


class Interface(object):
    window_width = None
    window_height = None
    zoom_exponent = 0
    _is_dragging = False
    drag_start = None
    delta_viewport_by_dragging = None
    _viewport_fixed_center = (0.0, 0.0)
    viewport_min_x = None
    viewport_max_x = None
    viewport_min_y = None
    viewport_max_y = None

    FAST_TRANSITION_TIME = 100
    SLOW_TRANSITION_TIME = 500

    show_fill = True

    show_wireframe = False
    VISIBLE_WIREFRAME_COLOR = [1.0, 1.0, 0.0, 1.0]
    HIDDEN_WIREFRAME_COLOR = [1.0, 1.0, 0.0, 0.0]

    show_points = False
    VISIBLE_POINT_BORDER_COLOR = [0.0, 0.0, 0.0, 1.0]
    HIDDEN_POINT_BORDER_COLOR = [0.0, 0.0, 0.0, 0.0]
    VISIBLE_POINT_FILL_COLOR = [1.0, 0.0, 0.0, 1.0]
    HIDDEN_POINT_FILL_COLOR = [1.0, 0.0, 0.0, 0.0]

    show_target = True
    VISIBLE_TARGET_COLOR = [0.0, 0.4, 0.8, 1.0]
    HIDDEN_TARGET_COLOR = [0.0, 0.4, 0.8, 0.0]

    @property
    def is_dragging(self):
        return self._is_dragging

    @property
    def viewport_fixed_center(self):
        return self._viewport_fixed_center

    @viewport_fixed_center.setter
    def viewport_fixed_center(self, value):
        self._viewport_fixed_center = value

    @property
    def viewport_center(self):
        if self._is_dragging:
            return (self._viewport_fixed_center[0]
                    - self.delta_viewport_by_dragging[0, 0],
                    self._viewport_fixed_center[1]
                    - self.delta_viewport_by_dragging[0, 1])
        return self._viewport_fixed_center

    def increment_zoom(self):
        self.zoom_exponent -= 1
        self.set_scene_coords_projection()

    def decrement_zoom(self):
        self.zoom_exponent += 1
        self.set_scene_coords_projection()

    @property
    def zoom_factor(self):
        return 1.2 ** (self.zoom_exponent + 0)

    def scene_to_window_coords(self, point, *args):
        return gluProject(point[0], point[1], point[2], *args)

    def window_to_viewport_coords(self, points):
        if isinstance(points, tuple):
            points = numpy.array(points).reshape(-1, 2).astype(float)

        # Normalize to [0, 1]
        points = points / [[self.window_width, self.window_height]]
        # Invert orientation of Y
        points[:, 1] = 1.0 - points[:, 1]
        # Normalize to [0, viewport_max_*-viewport_min_*]
        points *= [[self.viewport_max_x - self.viewport_min_x,
                    self.viewport_max_y - self.viewport_min_y]]
        # Shift to [viewport_min_*, viewport_max_*]
        points += [[self.viewport_min_x, self.viewport_min_y]]

        return points

    def set_scene_coords_projection(self, use_fixed_viewport_center=False):
        if self.window_width > self.window_height:
            delta_x = float(self.window_width) / float(self.window_height)
            delta_y = 1.
        else:
            delta_x = 1.
            delta_y = float(self.window_height) / float(self.window_width)

        if use_fixed_viewport_center:
            viewport_center = self._viewport_fixed_center
        else:
            viewport_center = self.viewport_center

        self.viewport_min_x = viewport_center[0] - delta_x * self.zoom_factor
        self.viewport_max_x = viewport_center[0] + delta_x * self.zoom_factor
        self.viewport_min_y = viewport_center[1] - delta_y * self.zoom_factor
        self.viewport_max_y = viewport_center[1] + delta_y * self.zoom_factor

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()

        glOrtho(self.viewport_min_x, self.viewport_max_x,
                self.viewport_min_y, self.viewport_max_y,
                -1, 1)

        glMatrixMode(GL_MODELVIEW)

    def set_window_coords_projection(self):
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()

        glOrtho(0, self.window_width,
                0, self.window_height,
                -1, 1)

        glMatrixMode(GL_MODELVIEW)

    def start_drag(self, x, y):
        self._is_dragging = True
        self.drag_start = self.window_to_viewport_coords((x, y))
        self.delta_viewport_by_dragging = numpy.array([[0., 0.]])

    def update_drag(self, x, y):
        if not self._is_dragging:
            return

        self.set_scene_coords_projection(use_fixed_viewport_center=True)
        current_drag = self.window_to_viewport_coords((x, y))
        self.delta_viewport_by_dragging = current_drag - self.drag_start

        self.set_scene_coords_projection()

    def finish_drag(self):
        if not self._is_dragging:
            return

        self._viewport_fixed_center = self.viewport_center
        self._is_dragging = False
        self.set_scene_coords_projection()

    def cancel_drag(self):
        self._is_dragging = False
        self.set_scene_coords_projection()


timing = Timing()

timing.set_value('main_opacity', 1.0)
timing.set_value('main_wireframe_color', Interface.HIDDEN_WIREFRAME_COLOR)
timing.set_value('point_border_color', Interface.HIDDEN_POINT_BORDER_COLOR)
timing.set_value('point_fill_color', Interface.HIDDEN_POINT_FILL_COLOR)
timing.set_value('target_wireframe_color', Interface.VISIBLE_TARGET_COLOR)


interface = Interface()
context = Context(config=config, interface=interface, timing=timing)


def display():
    timing.update_time()

    glClearColor(0.1, 0.1, 0.1, 1)
    if config.enable_depth:
        glClear(GL_COLOR_BUFFER_BIT + GL_DEPTH_BUFFER_BIT)
    else:
        glClear(GL_COLOR_BUFFER_BIT)

    interface.set_scene_coords_projection()
    glLoadIdentity()

    draw_grid_2d(grid_spacing=1)
    current_modelview_matrix = glGetFloatv(GL_MODELVIEW_MATRIX)
    current_projection_matrix = glGetFloatv(GL_PROJECTION_MATRIX)

    for instruction in config.sequence:
        glMatrixMode(GL_PROJECTION)
        glLoadMatrixf(current_projection_matrix)
        glMatrixMode(GL_MODELVIEW)
        glLoadMatrixf(current_modelview_matrix)

        command = instruction[0]

        if command == 'UserCallback':
            glColor(1, 1, 1, 1)
            compor_cena(context)

        elif command == 'Outline':
            glColor(timing.get_value('target_wireframe_color'))
            config.geometry.draw_wireframe(instruction[1])

        elif command == 'Fill':
            config.geometry.fill(instruction[1])

    glutSwapBuffers()


def idle():
    glutPostRedisplay()


def reshape(width, height):
    interface.window_width = width
    interface.window_height = height

    glViewport(0, 0, interface.window_width, interface.window_height)
    interface.set_scene_coords_projection()


def mouse(button, state, x, y):
    if button == GLUT_LEFT_BUTTON:
        if state == GLUT_DOWN:
            interface.start_drag(x, y)
        else:
            interface.finish_drag()

    elif button == 3:  # Scroll up
        interface.increment_zoom()

    elif button == 4:  # Scroll down
        interface.decrement_zoom()


def motion(x, y):
    interface.update_drag(x, y)


def keyboard(key, x, y):
    if key == b'\x1b':
        sys.exit(0)

    elif key == b'+' or key == b'=':
        interface.increment_zoom()

    elif key == b'-':
        interface.decrement_zoom()

    elif key.lower() == b'f':
        transition_time = interface.FAST_TRANSITION_TIME \
            if key == b'F' else interface.SLOW_TRANSITION_TIME

        if interface.show_fill:
            interface.show_fill = False
            timing.set_value('main_opacity', 0.1, transition_time)
        else:
            interface.show_fill = True
            timing.set_value('main_opacity', 1.0, transition_time)

    elif key.lower() == b'w':
        transition_time = interface.FAST_TRANSITION_TIME \
            if key == b'W' else interface.SLOW_TRANSITION_TIME

        if interface.show_wireframe:
            interface.show_wireframe = False
            timing.set_value('main_wireframe_color',
                             Interface.HIDDEN_WIREFRAME_COLOR,
                             transition_time)
        else:
            interface.show_wireframe = True
            timing.set_value('main_wireframe_color',
                             Interface.VISIBLE_WIREFRAME_COLOR,
                             transition_time)

    elif key.lower() == b'p':
        transition_time = interface.FAST_TRANSITION_TIME \
            if key == b'P' else interface.SLOW_TRANSITION_TIME

        if interface.show_points:
            interface.show_points = False
            timing.set_value('point_border_color',
                             Interface.HIDDEN_POINT_BORDER_COLOR,
                             transition_time)
            timing.set_value('point_fill_color',
                             Interface.HIDDEN_POINT_FILL_COLOR,
                             transition_time)
        else:
            interface.show_points = True
            timing.set_value('point_border_color',
                             Interface.VISIBLE_POINT_BORDER_COLOR,
                             transition_time)
            timing.set_value('point_fill_color',
                             Interface.VISIBLE_POINT_FILL_COLOR,
                             transition_time)

    elif key == b'[':
        context.prev_phase()

    elif key == b']':
        context.next_phase()

    elif key == b'{':
        context.first_phase()

    elif key == b'}':
        context.last_phase()

    else:
        processar_teclado(key)


if config.bounds_min is not None:
    bounds_min, bounds_max = config.bounds_min, config.bounds_max
else:
    bounds_min, bounds_max = config.geometry.get_bounds(config.fit_objects)

delta_x = bounds_max[0] - bounds_min[0]
delta_y = bounds_max[1] - bounds_min[1]
interface.zoom_exponent = max(math.log(delta_x / 2) / math.log(1.2),
                              math.log(delta_y / 2) / math.log(1.2)) + 1

if config.center is not None:
    interface.viewport_fixed_center = config.center
else:
    interface.viewport_fixed_center = (bounds_min[0] + 0.5 * delta_x,
                                       bounds_min[1] + 0.5 * delta_y)

glutInitWindowPosition(0, 0)
glutInitWindowSize(400, 400)
glutCreateWindow(b"Computer Graphics")

glEnable(GL_BLEND)
glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

if config.enable_depth:
    glEnable(GL_DEPTH_TEST)

glutDisplayFunc(display)
glutIdleFunc(idle)
glutReshapeFunc(reshape)
glutMouseFunc(mouse)
glutMotionFunc(motion)
glutKeyboardFunc(keyboard)

glutMainLoop()
