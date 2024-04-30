import sys
import pathlib
from copy import deepcopy
from enum import Enum
from PyQt5.QtCore import QObject, pyqtSlot, Qt, QDir, QPointF
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsView, QDialog, QFileDialog
from PyQt5.QtGui import QCursor

from ConfigureView.Grid2D import GraphicsPlotItem
from ConfigureView.GraphicComponents import *
from ConfigureView.GraphicComponentPresenter import *
from ConfigureView.Models import *
from ConfigureView.SaveLoader import SaveLoader

from ConfigureView.ConfigurationWindows import *
from ConfigureView.ConfigurationPresenters import *
from ConfigureView.CoordinatesTranslator import CoordinatesTranslator
from ConfigureView.MVPCreator import MVPCreator

world_max_coord = 100000

class Modes(Enum):
    DEFAULT = 1
    TRACK_CREATING = 2

class ConfiguratingViewport(QGraphicsView):
    def __init__(self, pixmaps, start_drag_distance, parent=None):
        super(ConfiguratingViewport, self).__init__(parent)
        self.mvp_creator = MVPCreator()
        self.models = [DispatcherSource()]
        self.presenters = list()
        self.pixmaps = pixmaps
        self.id_counter = 1
        self.start_drag_distance = start_drag_distance
        self.scene = QGraphicsScene()
        self.view = self
        self.view.setScene(self.scene)
        self.view.setGeometry(0, 0, 1150, 1150)
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        self.view.setMouseTracking(True)

        self.setGrid()
        self.translator = CoordinatesTranslator(self.plot.gridItem)

        self.view.show()

        self.config_windows = [ControlPointWindow(self), RadarWindow(self),
                              StartDeviceWindow(self), AeroTargetWindow(self), TrackPointWindow(self),
                              DispatcherConfigWindow(self)]
        self.dialog_presenters = [PosConfigPresenter(self.config_windows[0]),
                                 RadarConfigPresenter(self.config_windows[1]),
                                 PosConfigPresenter(self.config_windows[2]),
                                 AeroTargetConfigPresenter(self.config_windows[3]),
                                 PosConfigPresenter(self.config_windows[4]),
                                 DispatcherConfigPresenter(self.config_windows[-1], self.models[0])]

        self.mode = Modes.DEFAULT
        self.track_presenter = None

    def setGrid(self):
        self.plot = GraphicsPlotItem()
        self.scene.addItem(self.plot)
        self.plot.setRect(QRectF(0, 0, 1000, 1000))
        self.plot.setAxisText(0, "x, м")
        self.plot.setAxisText(1, "y, м")
        self.plot.setAbscissaRange(-world_max_coord, world_max_coord)
        self.plot.setOrdinateRange(-world_max_coord, world_max_coord)
        self.scene.setSceneRect(self.plot.boundingRect())

    def mouseMoveEvent(self, event):
        self.scene.update()
        super().mouseMoveEvent(event)
        if self.mode == Modes.TRACK_CREATING:
            p = self.view.mapToScene(event.pos())
            grid_pos = self.plot.gridItem.mapFromScene(p)
            if self.plot.gridItem.boundingRect().contains(grid_pos):
                pass
            else:
                self.track_presenter.target_presenter.onAddTrackCanceled()
                self.returnToNormalMode()

    def mousePressEvent(self, event):
        if self.mode == Modes.DEFAULT:
            super().mousePressEvent(event)
        elif self.mode == Modes.TRACK_CREATING:
            pass

    def mouseReleaseEvent(self, event):
        if self.mode == Modes.DEFAULT:
            super().mouseReleaseEvent(event)
        elif self.mode == Modes.TRACK_CREATING and event.button() == Qt.LeftButton:
            p = self.view.mapToScene(event.pos())
            grid_pos = self.plot.gridItem.mapFromScene(p)
            if self.plot.gridItem.boundingRect().contains(grid_pos):
                self.addPointWithLine(self.plot.gridItem.mapToScene(grid_pos))
                self.returnToNormalMode()

    def contextMenuEvent(self, event):
        if self.mode == Modes.DEFAULT:
            super().contextMenuEvent(event)
        elif self.mode == Modes.TRACK_CREATING:
            self.track_presenter.target_presenter.onAddTrackCanceled()
            self.returnToNormalMode()

    def leaveEvent(self, event):
        if self.mode != Modes.DEFAULT:
            self.track_presenter.target_presenter.onAddTrackCanceled()
            self.returnToNormalMode()
        super().leaveEvent(event)

    def resizeEvent(self, event):
        #new_size = event.size()
        #self.translator.setNewWidgetSize(new_size.width() // 2, new_size.height() // 2)
        #super().resizeEvent(event)
        self.view.fitInView(self.sceneRect(), Qt.KeepAspectRatio)
    
    def drawForeground(self, painter, rect):
        super().drawForeground(painter, rect)
        pos = self.view.mapToScene(self.view.mapFromGlobal(QCursor.pos()))
        grid_pos = self.plot.gridItem.mapFromScene(pos)
        if self.plot.gridItem.boundingRect().contains(grid_pos):
            painter.drawText(pos, f'X: {round(grid_pos.x())}, Y: {round(grid_pos.y())}')

    def getModelSources(self):
        return self.models

    #### slots

    @pyqtSlot(int)
    def addItem(self, model_type, x=0, y=0):
        model, component, presenter = self.mvp_creator.create(model_type, self.id_counter, x, y, 
                                                         self.translator, self.pixmaps[model_type // 1000],
                                                         self.start_drag_distance)
        self.models.append(model)
        self.scene.addItem(component)
        component.setPos(self.plot.gridItem.mapToScene(x, y))
        presenter.configurateRequested.connect(self.openConfigurationWindow)
        presenter.deleteRequested.connect(self.deleteItem)
        if isinstance(presenter, GraphicAeroTargetPresenter):
            presenter.track_presenter.addPointRequested.connect(self.onAddPointRequested)
            presenter.track_presenter.configurateRequested.connect(self.openPointConfigurationWindow)
            presenter.track_presenter.deleteRequested.connect(self.deletePointWithLine)
        self.presenters.append(presenter)
        self.id_counter += 1

    @pyqtSlot(QObject)
    def openConfigurationWindow(self, presenter):
        self.dialog_presenters[presenter.model.model_type // 1000 - 1].configurate(presenter.model)

    @pyqtSlot()
    def openModelingSettingsWindow(self):
        self.dialog_presenters[-1].configurate()

    @pyqtSlot(QObject)
    def deleteItem(self, presenter):
        self.models.remove(presenter.model)
        self.scene.removeItem(presenter.component)
        self.presenters.remove(presenter)
        presenter.configurateRequested.disconnect(self.openConfigurationWindow)
        presenter.deleteRequested.disconnect(self.deleteItem)
        if isinstance(presenter, GraphicAeroTargetPresenter):
            presenter.track_presenter.addPointRequested.disconnect(self.onAddPointRequested)
            presenter.track_presenter.configurateRequested.disconnect(self.openPointConfigurationWindow)
            presenter.track_presenter.deleteRequested.disconnect(self.deletePointWithLine)
        presenter.delSelf()

    @pyqtSlot(QObject)
    def onAddPointRequested(self, presenter):
        self.mode = Modes.TRACK_CREATING
        self.track_presenter = presenter
        self.setCursor(Qt.CrossCursor)

    def returnToNormalMode(self):
        self.mode = Modes.DEFAULT
        self.track_presenter = None
        self.setCursor(Qt.ArrowCursor)

    def addPointWithLine(self, pos):
        line = LineGraphicComponent()
        component = PointGraphicComponent(self.start_drag_distance, self.plot.gridItem)

        self.scene.addItem(component)
        self.scene.addItem(line)

        component.setPos(pos)
        model = PointSource(0, 0)
        self.track_presenter.onAddPoint(model, component, line)

    @pyqtSlot(QObject)
    def openPointConfigurationWindow(self, point):
        self.dialog_presenters[4].configurate(point)

    @pyqtSlot(object)
    def deletePointWithLine(self, objects):
        for obj in objects:
            self.scene.removeItem(obj)

    @pyqtSlot()
    def onConfigurationSaveClicked(self):
        file_name = QFileDialog.getSaveFileName(filter='Text files (*.txt)')[0]
        if file_name:
            SaveLoader.saveObjects(self.models, file_name)

    @pyqtSlot()
    def onConfigurationLoadClicked(self):
        file_name = QFileDialog.getOpenFileName(filter='Text files (*.txt)')[0]
        if file_name:
            presenter_list = self.presenters[-1::-1]
            for presenter in presenter_list:
                if isinstance(presenter, GraphicAeroTargetPresenter):
                    presenter.track_presenter.onAllDeleteRequested()
                self.deleteItem(presenter)

            self.models = SaveLoader.uploadObjects(file_name)
            self.dialog_presenters[-1].dispatcher = self.models[0]
            self.dialog_presenters[-1].updateUIFields()

            for model in self.models[1:]:
                self.id_counter = max(self.id_counter, model.id)
                component, presenter = self.mvp_creator.createByModel(model, self.translator, 
                                                                         self.pixmaps[model.model_type // 1000], self.start_drag_distance)
                self.scene.addItem(component)
                component.setPos(self.plot.gridItem.mapToScene(model.getX(), model.getY()))
                presenter.configurateRequested.connect(self.openConfigurationWindow)
                presenter.deleteRequested.connect(self.deleteItem)
                if isinstance(presenter, GraphicAeroTargetPresenter):
                    presenter.track_presenter.addPointRequested.connect(self.onAddPointRequested)
                    presenter.track_presenter.configurateRequested.connect(self.openPointConfigurationWindow)
                    presenter.track_presenter.deleteRequested.connect(self.deletePointWithLine)
                    points = model.track.points
                    model.track.deleteAllPoint()
                    self.track_presenter = presenter.track_presenter
                    for point in points:
                        self.addPointWithLine(self.plot.gridItem.mapToScene((QPointF(point.getX(), point.getY()))))
                    self.track_presenter = None

                presenter.updateUI()
                self.presenters.append(presenter)

