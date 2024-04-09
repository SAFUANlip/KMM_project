import sys
import pathlib
from copy import deepcopy

from PyQt5.QtCore import QObject, pyqtSlot, Qt
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsView, QDialog

from ConfigureView.Grid2D import GraphicsPlotItem
from ConfigureView.GraphicComponents import *
from ConfigureView.GraphicComponentPresenter import *
from ConfigureView.Models import *

from ConfigureView.ConfigurationWindows import *
from ConfigureView.ConfigurationPresenters import *
from ConfigureView.CoordinatesTranslator import CoordinatesTranslator
from ConfigureView.MVPCreator import MVPCreator

world_max_coord = 300000

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

        self.setGrid()
        self.translator = CoordinatesTranslator(self.plot.gridItem)

        self.view.show()

        self.config_windows = [ControlPointWindow(self), RadarWindow(self),
                              StartDeviceWindow(self), AeroTargetWindow(self),
                              DispatcherConfigWindow(self)]
        self.dialog_presenters = [PosConfigPresenter(self.config_windows[0]),
                                 RadarConfigPresenter(self.config_windows[1]),
                                 PosConfigPresenter(self.config_windows[2]),
                                 AeroTargetConfigPresenter(self.config_windows[3]),
                                 DispatcherConfigPresenter(self.config_windows[-1], self.models[0])]

    def setGrid(self):
        self.plot = GraphicsPlotItem()
        self.scene.addItem(self.plot)
        self.plot.setRect(QRectF(0, 0, 1000, 1000))
        self.plot.setAxisText(0, "x, м")
        self.plot.setAxisText(1, "y, м")
        self.plot.setAbscissaRange(-300000, 300000)
        self.plot.setOrdinateRange(-300000, 300000)
        self.scene.setSceneRect(self.plot.boundingRect())

    def resizeEvent(self, event):
        #new_size = event.size()
        #self.translator.setNewWidgetSize(new_size.width() // 2, new_size.height() // 2)
        #super().resizeEvent(event)
        self.view.fitInView(self.sceneRect(), Qt.KeepAspectRatio)
    
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
        presenter.delSelf()