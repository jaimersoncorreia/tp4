from OpenGL.GL import *

from drawingutils import *


class Context(object):
    def __init__(self, config, interface, timing):
        self._config = config
        self._interface = interface
        self._timing = timing
        self._geometry = config.geometry
        self._current_phase = 0

        self._timing.set_value("phase", 0)

    def get_phase_k(self, phase):
        phase = float(phase)
        running_phase = self._timing.get_value("phase")

        if running_phase <= phase:
            return 0.0
        elif running_phase >= phase + 1.0:
            return 1.0
        else:
            return running_phase - phase

    @property
    def object_names(self):
        return self._geometry.object_names

    def draw(self, object_name=None):
        if object_name is None:
            object_name = self._config.default_object_name

        self._geometry.fill(object_name,
                            opacity=self._timing.get_value('main_opacity'))
        glColor(self._timing.get_value('main_wireframe_color'))
        self._geometry.draw_wireframe(object_name)

        # modelview_matrix = glGetDoublev(GL_MODELVIEW_MATRIX)
        # projection_matrix = glGetDoublev(GL_PROJECTION_MATRIX)
        # viewport_matrix = glGetIntegerv(GL_VIEWPORT)
        #
        # self._interface.set_window_coords_projection()
        #
        # glColor(self._timing.get_value('point_fill_color'))
        # for point in self._geometry.get_vertexes(object_name):
        #     fill_circle(5, self._interface.scene_to_window_coords(
        #         point, modelview_matrix, projection_matrix, viewport_matrix))
        # glColor(self._timing.get_value('point_border_color'))
        # for point in self._geometry.get_vertexes(object_name):
        #     draw_circle(5, self._interface.scene_to_window_coords(
        #         point, modelview_matrix, projection_matrix, viewport_matrix))

    def outline(self, object_name=None, color=None):
        if object_name is None:
            object_name = self._config.default_object_name
        if color is None:
            color = (0.2, 0.6, 0.8)

        glColor(color)
        self._geometry.draw_wireframe(object_name)

    def first_phase(self):
        if self._current_phase > 0:
            self._current_phase = 0
            self._timing.set_value("phase", float(self._current_phase))

    def last_phase(self):
        if self._config.phase_count is None \
                or self._current_phase < self._config.phase_count:
            self._current_phase = self._config.phase_count
            self._timing.set_value("phase", float(self._current_phase), 0.0)

    def next_phase(self):
        if self._config.phase_count is None \
                or self._current_phase < self._config.phase_count:
            self._current_phase += 1
            self._timing.set_value("phase", float(self._current_phase), 1000.0)

    def prev_phase(self):
        if self._current_phase > 0:
            self._current_phase -= 1
            self._timing.set_value("phase", float(self._current_phase), 100.0)
