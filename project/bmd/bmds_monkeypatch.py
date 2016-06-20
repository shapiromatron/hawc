import bmds


# monkey-patch execution in bmds package
def execute(self):
    print('hi!')


bmds.BMDModel.execute = execute
