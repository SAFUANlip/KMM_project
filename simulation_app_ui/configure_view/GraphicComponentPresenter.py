from PyQt5.QtCore import QObject
from PyQt5.QtCore import pyqtSignal, pyqtSlot
from simulation_app_ui.configure_view.GraphicComponents import PointGraphicComponent

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
            start_angle = self.model.pan_start #-self.model.pan_start + 90 - span // 2
            self.component.setSector(start_angle, span)
            self.component.whole_sector.hide()
        else:
            self.component.round.hide()
            self.component.sector.hide()
            self.component.whole_sector.show()
            span = self.model.pan_angle
            start_angle = self.model.pan_start #-self.model.pan_start + 90 - span // 2
            self.component.setWholeSector(start_angle, span)


class GraphicTrackPresenter(QObject):

    addPointRequested = pyqtSignal(QObject)
    configurateRequested = pyqtSignal(QObject)
    deleteRequested = pyqtSignal(object)

    def __init__(self, translator, target_presenter):
        super(GraphicTrackPresenter, self).__init__()
        self.target_presenter = target_presenter
        self.track = target_presenter.model.track
        self.points = dict()
        self.translator = translator
        self.track.dataChanged.connect(self.updateUI)
        self.translator.scaleChanged.connect(self.updateUI)

    def delSelf(self):
        self.translator.scaleChanged.disconnect(self.updateUI)

    #### slots
    @pyqtSlot()
    def updateUI(self):
        for component, model in self.points.items():
            point = self.translator.translateFromModel(model.getX(), model.getY())
            component.setPos(point.x(), point.y())
            component.is_collided = model.checkCollisions()

    @pyqtSlot()
    def onComponentDragged(self):
        for component, model in self.points.items():
            point = self.translator.translateToModel(component.x(), component.y())
            model.setX(point.x())
            model.setY(point.y())
            component.is_collided = model.checkCollisions()
        self.track.onTrackStateChanged()

    def onAddPoint(self, point_model, point_component, line):
        last = self.track.getLastPoint()
        
        if last:
            last_component = list(self.points.keys())[list(self.points.values()).index(last)] # берем ключ по значению
            line.left_point = last_component
            last_component.right_line = line
        else:
            line.left_point = self.target_presenter.component
        
        point_component.left_line = line
        line.right_point = point_component
        
        coord = self.translator.translateToModel(point_component.x(), point_component.y())
        point_model.setX(coord.x())
        point_model.setY(coord.y())
        self.track.addPoint(point_model)
        self.points[point_component] = point_model
        point_component.posChanged.connect(self.onComponentDragged)
        point_component.configurateRequested.connect(self.onConfigurateClicked)
        point_component.deleteRequest.connect(self.onDeleteClicked)
        point_component.addPointRequest.connect(lambda: self.addPointRequested.emit(self))

    @pyqtSlot(QObject)
    def onConfigurateClicked(self, graphic_component):
        self.configurateRequested.emit(self.points[graphic_component])

    @pyqtSlot(QObject)
    def onDeleteClicked(self, graphic_component):
        self.track.deletePoint(self.points[graphic_component])
        deletion = [graphic_component]
        if graphic_component.right_line:
            graphic_component.left_line.right_point = graphic_component.right_line.right_point
            graphic_component.right_line.right_point.left_line = graphic_component.left_line
            deletion.append(graphic_component.right_line)
        else:
            if isinstance(graphic_component.left_line.left_point, PointGraphicComponent):
                graphic_component.left_line.left_point.right_line = None
            deletion.append(graphic_component.left_line)
        graphic_component.posChanged.disconnect()
        graphic_component.configurate_action.triggered.disconnect()
        graphic_component.del_action.triggered.disconnect()
        graphic_component.addPointRequest.disconnect()

        self.target_presenter.onAddTrackCanceled()

        self.deleteRequested.emit(deletion)

    def onAllDeleteRequested(self):
        self.track.deleteAllPoint()
        lines = [component.left_line for component in self.points]
        if lines:
            lines[0].left_point = None # Предосторожность, чтобы gc уж точно уничтожил линию соед воздушную цель и точку
            self.deleteRequested.emit(lines + [*self.points])


class GraphicAeroTargetPresenter(GraphicComponentPresenter):
    def __init__(self, model, component, translator):
        super(GraphicAeroTargetPresenter, self).__init__(model, component, translator)
        self.component.add_track_action.triggered.connect(self.onAddTrackClicked)
        self.component.del_track_action.triggered.connect(self.onDelTrackClicked)
        self.track_presenter = GraphicTrackPresenter(translator, self)

    @pyqtSlot()
    def updateUI(self):
        super().updateUI()
        self.component.setRotation(self.model.direction)

    @pyqtSlot()
    def onAddTrackClicked(self):
        self.component.add_track_action.setVisible(False)
        self.component.del_track_action.setVisible(True)
        self.track_presenter.addPointRequested.emit(self.track_presenter)

    def onAddTrackCanceled(self):
        if self.track_presenter.track.isEmpty():
            self.component.add_track_action.setVisible(True)
            self.component.del_track_action.setVisible(False)
        
    @pyqtSlot()
    def onDelTrackClicked(self):
        self.component.add_track_action.setVisible(True)
        self.component.del_track_action.setVisible(False)
        self.track_presenter.onAllDeleteRequested()

    @pyqtSlot()
    def onDeleteClicked(self):
        self.track_presenter.onAllDeleteRequested()
        self.deleteRequested.emit(self)