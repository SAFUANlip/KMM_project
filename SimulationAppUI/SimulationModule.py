from PyQt5.QtWidgets import QApplication
import sys

from PyQt5.QtWidgets import QProgressDialog
from PyQt5.QtCore import Qt, QThread, QObject, pyqtSlot, pyqtSignal, QTimer
import numpy as np
from math import floor

from src.modules_classes.AeroEnv import *
from src.modules_classes.CombatControPoint import *
from src.modules_classes.Radar import *
from src.modules_classes.StartingDevice import *
from src.modules_classes.ModelDispatcher import *

class CustomThread(QThread):
    def __init__(self, target=None):
        super(CustomThread, self).__init__()
        self.target = target
    
    def run(self):
        if self.target:
            self.target()

class SimulationModule(QObject):

    simulationEnded = pyqtSignal(object)

    def __init__(self, parent=None):
        super(SimulationModule, self).__init__()
        self.window = QProgressDialog(minimum=0, maximum=100, parent=parent)
        self.window.setWindowFlags(self.window.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.window.setWindowTitle("Моделирование")
        self.window.setMinimumWidth(300)
        self.window.findChild(QTimer).stop()
        self.window.canceled.connect(self.onCancel)
        self.thread = None
        self.dispatcher = None

    def buildModels(self, model_sources):
        dispatcher = ModelDispatcher()
        dispatcher.setSimulatingRate(10)
        dispatcher.setSimulationTime(model_sources[0].getTime())

        # targets
        targets = list()

        for t_s in [model_source for model_source in model_sources[1:] if model_source.model_type // 1000 == 4]:
            vel = [t_s.speed * np.cos(t_s.direction * np.pi/180), t_s.speed * np.sin(t_s.direction * np.pi/180), 0]
            targets.append(Airplane(dispatcher, t_s.id, np.array([t_s.x, t_s.y, t_s.z]), 5, np.array(vel),
                                    t_s.time_start, t_s.time_finish))

        env = AeroEnv(dispatcher, -2)
        for target in targets:
            env.addEntity(target)

        configuration = [env]

        # starting devices
        sd_info = {}
        for sd_s in [model_source for model_source in model_sources[1:] if model_source.model_type // 1000 == 3]:
            pos = np.array([sd_s.x, sd_s.y, sd_s.z])
            sd_info[sd_s.id] = pos
            configuration.append(StartingDevice(dispatcher, sd_s.id, pos, env))

        cp_source = [model_source for model_source in model_sources[1:] if model_source.model_type // 1000 == 1][0]

        # radars
        for r_s in [model_source for model_source in model_sources[1:] if model_source.model_type // 1000 == 2]:
            radar_class = RadarRound
            if r_s.overview_mode != 0:
                radar_class = RadarSector
            configuration.append(radar_class(dispatcher, r_s.id, cp_source.id, env, np.array([r_s.x, r_s.y, r_s.z]), 
                                             r_s.pan_start * np.pi/180, r_s.tilt_start * np.pi/180, r_s.view_distance,
                                             r_s.pan_per_sec * np.pi/180, r_s.tilt_per_sec * np.pi/180))

        # CP
        configuration.append(CombatControlPoint(dispatcher, cp_source.id, sd_info))
        dispatcher.configurate(configuration)
        return dispatcher

    def startSimulation(self, model_sources):
        self.dispatcher = self.buildModels(model_sources)
        self.dispatcher.tick.connect(self.updateProgress)
        self.thread = CustomThread(self.dispatcher.run)
        self.thread.finished.connect(self.onSimulationEnded)
        self.window.setValue(0)
        self.window.setMaximum(floor(model_sources[0].getTime() * 10))
        self.thread.start()
        self.window.exec_()

    @pyqtSlot(int)
    def updateProgress(self, step):
        self.window.setValue(step)

    @pyqtSlot()
    def onCancel(self):
        self.thread.finished.disconnect(self.onSimulationEnded)
        self.dispatcher.tick.disconnect(self.updateProgress)
        self.dispatcher.stop()
        self.thread.deleteLater()
        self.dispatcher.deleteLater()
        self.thread = None
        self.dispatcher = None

    @pyqtSlot()
    def onSimulationEnded(self):
        result = self.dispatcher.getMessageHistory()[1]
        self.thread.finished.disconnect(self.onSimulationEnded)
        self.dispatcher.tick.disconnect(self.updateProgress)
        self.thread.deleteLater()
        self.dispatcher.deleteLater()
        self.thread = None
        self.dispatcher = None
        self.simulationEnded.emit(result)