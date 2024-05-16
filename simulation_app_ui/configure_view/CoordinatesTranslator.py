from PyQt5.QtCore import QObject, pyqtSignal

class CoordinatesTranslator(QObject):

    scaleChanged = pyqtSignal()

    def __init__(self, grid):
        super(CoordinatesTranslator, self).__init__()
        self.grid = grid

    def translateToModel(self, x, y):
        return self.grid.mapFromScene(x, y)

    def translateFromModel(self, x, y):
        return self.grid.mapToScene(x, y)