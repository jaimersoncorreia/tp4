from OpenGL.GL import *
from OpenGL.GLUT import *


class Timing(object):
    def __init__(self):
        self._last_time = glutGet(GLUT_ELAPSED_TIME)
        self._items = {}

    @staticmethod
    def interpolate(a, b, t):
        if isinstance(a, tuple):
            return tuple(map(
                lambda index: Timing.interpolate(a[index], b[index], t),
                range(len(a))))

        if isinstance(a, list):
            return list(map(
                lambda index: Timing.interpolate(a[index], b[index], t),
                range(len(a))))

        return (1.0 - t) * a + t * b

    @property
    def last_time(self):
        return self._last_time

    def update_time(self):
        self._last_time = glutGet(GLUT_ELAPSED_TIME)

    def get_value(self, key):
        item_data = self._items[key]
        if item_data['future'] is None:
            return item_data['previous']
        if self.last_time >= item_data['future_time']:
            self._items[key] = {
                'previous': item_data['future'],
                'future': None,
            }
            return item_data['future']

        t = (float(self.last_time - item_data['previous_time'])
             / (item_data['future_time'] - item_data['previous_time']))
        return self.interpolate(item_data['previous'],
                                item_data['future'],
                                t)

    def set_value(self, key, value, time_ahead=0):
        if key not in self._items or time_ahead <= 0:
            self._items[key] = {'previous': value, 'future': None}
            return

        self._items[key] = {
            'previous': self.get_value(key),
            'previous_time': self.last_time,
            'future': value,
            'future_time': self.last_time + time_ahead,
        }
