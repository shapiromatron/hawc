from bmds import *   # noqa


# monkey-patch execution in bmds package
def execute(self):
    print('hi!')


BMDModel.execute = execute
