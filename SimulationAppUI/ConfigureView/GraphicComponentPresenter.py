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
        point = self.translator.translateFromModel(self.model.getX(), self.model.getY())
        self.component.setPos(point.x(), point.y())

    @pyqtSlot()
    def onComponentDragged(self):
        point = self.translator.translateToModel(self.component.x(), self.component.y())
        self.model.setX(point.x())
        self.model.setY(point.y())

    @pyqtSlot()
    def onConfigurateClicked(self):
        self.configurateRequested.emit(self)

    @pyqtSlot()
    def onDeleteClicked(self):
        self.deleteRequested.emit(self)


class GraphicRadarPresenter(GraphicComponentPresenter):
    def __init__(self, model, component, translator):
        super(GraphicRadarPresenter, self).__init__(model, component, translator)

        coord = (self.translator.translateFromModel(self.model.view_distance, self.model.view_distance) - 
                self.translator.translateFromModel(0, 0)).x()
        self.component.round.setRect(-coord, -coord, 2 * coord, 2 * coord)
        self.component.round.setParentItem(self.component)
        self.component.sector.setRect(-coord, -coord, 2 * coord, 2 * coord)
        self.component.sector.setParentItem(self.component)
        self.component.whole_sector.setRect(-coord, -coord, 2 * coord, 2 * coord)
        self.component.whole_sector.setParentItem(self.component)
        
        self.setSectorView()

    @pyqtSlot()
    def updateUI(self):
        super().updateUI()
        self.setSectorView()

    def setSectorView(self):
        if self.model.overview_mode == 0:
            self.component.round.show()
            self.component.sector.show()
            span = self.model.pan_per_sec
            start_angle = -self.model.pan_start + 90 - span // 2
            self.component.setSector(start_angle, span)
            self.component.whole_sector.hide()
        else:
            self.component.round.hide()
            self.component.sector.hide()
            self.component.whole_sector.show()
            span = self.model.pan_angle
            start_angle = -self.model.pan_start + 90 - span // 2
            self.component.setWholeSector(start_angle, span)


class GraphicAeroTargetPresenter(GraphicComponentPresenter):
    def __init__(self, model, component, translator):
        super(GraphicAeroTargetPresenter, self).__init__(model, component, translator)

    @pyqtSlot()
    def updateUI(self):
        super().updateUI()
        self.component.setRotation(self.model.direction)