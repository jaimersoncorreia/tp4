import math
import numpy

from OpenGL.GL import *


def fill_circle(radius, center=(0.0, 0.0, 0.0), steps=32):
    glBegin(GL_POLYGON)

    for step in range(steps):
        glVertex(radius * math.cos(step * 2 * math.pi / steps) + center[0],
                 radius * math.sin(step * 2 * math.pi / steps) + center[1],
                 center[2])

    glEnd()


def draw_circle(radius, center=(0.0, 0.0, 0.0), steps=32):
    glBegin(GL_LINE_LOOP)

    for step in range(steps):
        glVertex(radius * math.cos(step * 2 * math.pi / steps) + center[0],
                 radius * math.sin(step * 2 * math.pi / steps) + center[1],
                 center[2])

    glEnd()


def draw_grid_2d(grid_spacing=None):
    orig_depth_test_enabled = glIsEnabled(GL_DEPTH_TEST)
    modelview_matrix = numpy.array(glGetFloatv(GL_MODELVIEW_MATRIX))
    projection_matrix = numpy.array(glGetFloatv(GL_PROJECTION_MATRIX))
    inv_matrix = numpy.linalg.inv(projection_matrix.dot(modelview_matrix))

    glDisable(GL_DEPTH_TEST)

    scene_points = numpy.array(
        [[x, y, 0, 1] for x in (-1, 1) for y in (-1, 1)])
    image_points = scene_points.dot(inv_matrix)
    image_x = image_points[:, 0] / image_points[:, 3]
    image_y = image_points[:, 1] / image_points[:, 3]

    min_x = min(image_x)
    max_x = max(image_x)
    min_y = min(image_y)
    max_y = max(image_y)

    def get_grid_spacing(delta, min_intervals, factors):
        selected_interval_count = float('inf')
        selected_spacing = None

        for factor in factors:
            spacing = delta / min_intervals / factor
            spacing = 10 ** math.floor(math.log10(spacing)) * factor
            interval_count = delta / spacing

            if interval_count < selected_interval_count:
                selected_interval_count = interval_count
                selected_spacing = spacing

        return selected_spacing

    if grid_spacing is None:
        grid_spacing = get_grid_spacing(
            min(max_x - min_x, max_y - min_y), 10, (1, 2, 5))

    count_x = long(math.ceil(max_x / grid_spacing)
                   - math.floor(min_x / grid_spacing))
    min_x = math.floor(min_x / grid_spacing) * grid_spacing
    max_x = math.ceil(max_x / grid_spacing) * grid_spacing
    count_y = long(math.ceil(max_y / grid_spacing)
                   - math.floor(min_y / grid_spacing))
    min_y = math.floor(min_y / grid_spacing) * grid_spacing
    max_y = math.ceil(max_y / grid_spacing) * grid_spacing

    glColor(0.2, 0.2, 0.2)
    glBegin(GL_LINES)

    for index_y in range(count_y + 1):
        y = min_y + grid_spacing * index_y
        glVertex(min_x, y)
        glVertex(max_x, y)

    for index_x in range(count_x + 1):
        x = min_x + grid_spacing * index_x
        glVertex(x, min_y)
        glVertex(x, max_y)

    glColor(0.6, 0.2, 0.2)
    glVertex(min_x, 0)
    glVertex(max_x, 0)

    glColor(0.2, 0.6, 0.2)
    glVertex(0, min_y)
    glVertex(0, max_y)

    glEnd()

    if orig_depth_test_enabled:
        glEnable(GL_DEPTH_TEST)
