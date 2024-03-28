import sys
import pathlib

from PyQt5.QtCore import QObject, pyqtSlot, Qt
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsView, QDialog

from GraphicComponents import *
from GraphicComponentPresenter import *
from Models import *

from ConfigurationWindows import *
from ConfigurationPresenters import *
from CoordinatesTranslator import CoordinatesTranslator
from MVPCreator import MVPCreator

world_max_coord = 300000

class ConfiguratingViewport(QGraphicsView):
    def __init__(self, pixmaps, start_drag_distance, parent=None):
        super(ConfiguratingViewport, self).__init__(parent)
        self.translator = CoordinatesTranslator(768 // 2, 768 // 2,
                                                world_max_coord, world_max_coord)
        self.mvp_creator = MVPCreator()
        self.models = list()
        self.presenters = list()
        self.pixmaps = pixmaps
        self.id_counter = 1
        self.start_drag_distance = start_drag_distance
        #self.scene = QGraphicsScene(0, 0, self.size().width(), self.size().height())
        self.scene = QGraphicsScene(0, 0, 768, 768)
        self.view = self
        self.view.setScene(self.scene)
        self.view.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        self.view.setResizeAnchor(QGraphicsView.AnchorViewCenter)
        self.view.setAlignment(Qt.AlignCenter)
        self.view.show()

        self.config_windows = [ControlPointWindow(self), RadarWindow(self),
                              StartDeviceWindow(self), AeroTargetWindow(self)]
        self.dialog_presenters = [PosConfigPresenter(self.config_windows[0]),
                                 RadarConfigPresenter(self.config_windows[1]),
                                 PosConfigPresenter(self.config_windows[2]),
                                 AeroTargetConfigPresenter(self.config_windows[3])]


    def resizeEvent(self, event):
        new_size = event.size()
        #self.translator.setNewWidgetSize(new_size.width() // 2, new_size.height() // 2)
        super().resizeEvent(event)

    def addItem(self, model_type, x, y):
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

    #### slots

    @pyqtSlot(QObject)
    def openConfigurationWindow(self, presenter):
        self.dialog_presenters[presenter.model.model_type // 1000 - 1].configurate(presenter.model)

    @pyqtSlot(QObject)
    def deleteItem(self, presenter):
        self.models.remove(presenter.model)
        self.scene.removeItem(presenter.component)
        self.presenters.remove(presenter)
        presenter.configurateRequested.disconnect(self.openConfigurationWindow)
        presenter.deleteRequested.disconnect(self.deleteItem)
        presenter.delSelf()

    @pyqtSlot()
    def test(self):
        print("editingFinished()")