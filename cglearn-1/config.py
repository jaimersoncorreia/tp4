import sys
import os

from geometry import Geometry

try:
    import simplejson as json
except ImportError:
    import json


class Configuration(object):
    center = None
    bounds_min = None
    bounds_max = None

    def __init__(self, filepath):
        config_data = json.load(open(filepath))

        self.default_object_name = config_data.get("default_object")
        self.phase_count = config_data.get("phases")
        self.module_name = config_data.get("module", "student_module")
        self.callback_name = config_data.get("callback", "compor_cena")
        self.enable_depth = config_data.get("depth", False)

        self.geometry = Geometry()

        obj_filepaths = config_data.get("obj_files", [])
        for obj_filepath in obj_filepaths:
            self.geometry.read_obj(obj_filepath)

        self.fit_objects = config_data.get("fit_objects")
        self.sequence = config_data.get("sequence", ["UserCallback"])

        center = config_data.get("center")
        if center is not None:
            self.center = tuple(map(float, center))

        bounds = config_data.get("bounds")
        if bounds is not None:
            self.bounds_min = (float(min(bounds[0][0], bounds[1][0])),
                               float(min(bounds[0][1], bounds[1][1])))
            self.bounds_max = (float(max(bounds[0][0], bounds[1][0])),
                               float(max(bounds[0][1], bounds[1][1])))


def get_config_filepaths():
    entries = os.listdir('.')
    entries = [entry for entry in entries
               if os.path.isfile(entry)
               and os.path.splitext(entry)[1] == '.json']
    return entries


def load_config_file(filepath=None):
    if filepath is None:
        filepaths = get_config_filepaths()

        if not filepaths:
            raise IOError("Nenhum arquivo de configuracao foi encontrado.")

        if len(filepaths) > 1:
            print("Varios arquivos de configuracao foram encontrados."
                  " As opcoes sao:")
            print()

            for index, filepath in enumerate(filepaths, 1):
                print("  [%d] %s" % (index, filepath))
            print()

            print("Qual o arquivo a ser carregado? ", end='')
            sys.stdout.flush()
            index = int(sys.stdin.readline().strip())
            filepath = filepaths[index - 1]

        else:
            filepath = filepaths[0]

    return Configuration(filepath)
