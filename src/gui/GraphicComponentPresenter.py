from PyQt5.QtCore import QObject
from PyQt5.QtCore import pyqtSignal, pyqtSlot

class GraphicComponentPresenter(QObject):

    configurateRequested = pyqtSignal(QObject)
    deleteRequested = pyqtSignal(QObject)

    def __init__(self, model, component, translator):
        super(GraphicComponentPresenter, self).__init__()
        self.translator = translator
        self.model = model
        self.model.dataChanged.connect(self.updateUI)

        self.component = component
        self.component.posChanged.connect(self.onComponentDragged)
        self.component.configurate_action.triggered.connect(self.onConfigurateClicked)
        self.component.del_action.triggered.connect(self.onDeleteClicked)

        self.translator.scaleChanged.connect(self.updateUI)

    def delSelf(self):
        self.model.deleteLater()
        self.component.deleteLater()
        self.translator.scaleChanged.disconnect(self.updateUI)
        self.deleteLater()

    #### slots
    @pyqtSlot()
    def updateUI(self):
        x, y = self.translator.translateWorld2Screen(self.model.getX(), self.model.getY())
        self.component.setPos(x, y)

    @pyqtSlot()
    def onComponentDragged(self):
        x, y = self.translator.translateScreen2World(self.component.x(), self.component.y())
        self.model.setX(x)
        self.model.setY(y)

    @pyqtSlot()
    def onConfigurateClicked(self):
        self.configurateRequested.emit(self)

    @pyqtSlot()
    def onDeleteClicked(self):
        self.deleteRequested.emit(self)


class GraphicAeroTargetPresenter(GraphicComponentPresenter):
    def __init__(self, model, component, translator):
        super(GraphicAeroTargetPresenter, self).__init__(model, component, translator)

    @pyqtSlot()
    def updateUI(self):
        super().updateUI()
        self.component.setRotation(self.model.direction)