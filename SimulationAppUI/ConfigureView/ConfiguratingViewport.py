import sys
import pathlib
from copy import deepcopy

from PyQt5.QtCore import QObject, pyqtSlot, Qt
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsView, QDialog

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
        self.translator = CoordinatesTranslator(768 // 2, 768 // 2,
                                                world_max_coord, world_max_coord)
        self.mvp_creator = MVPCreator()
        self.models = [DispatcherSource()]
        self.presenters = list()
        self.pixmaps = pixmaps
        self.id_counter = 1
        self.start_drag_distance = start_drag_distance
        #self.scene = QGraphicsScene(0, 0, self.size().width(), self.size().height())
        self.scene = QGraphicsScene(0, 0, 768, 768)
        self.view = self
        self.view.setScene(self.scene)
        self.view.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        self.view.setResizeAnchor(QGraphicsView.NoAnchor)
        self.view.setAlignment(Qt.AlignLeft|Qt.AlignTop)
        self.view.show()

        self.config_windows = [ControlPointWindow(self), RadarWindow(self),
                              StartDeviceWindow(self), AeroTargetWindow(self),
                              DispatcherConfigWindow(self)]
        self.dialog_presenters = [PosConfigPresenter(self.config_windows[0]),
                                 RadarConfigPresenter(self.config_windows[1]),
                                 PosConfigPresenter(self.config_windows[2]),
                                 AeroTargetConfigPresenter(self.config_windows[3]),
                                 DispatcherConfigPresenter(self.config_windows[-1], self.models[0])]




    def resizeEvent(self, event):
        new_size = event.size()
        self.translator.setNewWidgetSize(new_size.width() // 2, new_size.height() // 2)
        super().resizeEvent(event)
    
    def getModelSources(self):
        return self.models

    #### slots

    @pyqtSlot(int)
    def addItem(self, model_type, x=None, y=None):
        if x is None or y is None:
            x, y = self.size().width() // 2, self.size().height() // 2
        model, component, presenter = self.mvp_creator.create(model_type, self.id_counter, x, y, 
                                                         self.translator, self.pixmaps[model_type // 1000],
                                                         self.start_drag_distance)
        self.models.append(model)
        component.setPos(x, y)
        self.scene.addItem(component)
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