from PyQt5.QtWidgets import QApplication
import sys

from PyQt5.QtWidgets import QProgressDialog, QMessageBox
from PyQt5.QtCore import Qt, QThread, QObject, pyqtSlot, pyqtSignal, QTimer
import numpy as np
from math import floor
from enum import Enum

from src.modules_classes.AeroEnv import *
from src.modules_classes.CombatControPoint import *
from src.modules_classes.Radar import *
from src.modules_classes.StartingDevice import *
from src.modules_classes.ModelDispatcher import *

class STATUS(Enum):
    NO_ERROR = 1
    BAD_TRACE_CONFIG = 2

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
        self.status = STATUS.NO_ERROR

    def buildModels(self, model_sources):
        self.status = STATUS.NO_ERROR

        dispatcher = ModelDispatcher()
        dispatcher.setSimulatingRate(10)
        dispatcher.setSimulationTime(model_sources[0].getTime())

        # targets
        targets = list()

        for t_s in [model_source for model_source in model_sources[1:] if model_source.model_type // 1000 == 4]:
            trace = [np.array([t_s.x, t_s.y, t_s.z])]
            if t_s.track.is_good:
                for point in t_s.track.points:
                    trace.append(np.array([point.getX(), point.getY(), point.getZ()]))
            else:
                self.status = STATUS.BAD_TRACE_CONFIG

            targets.append(
                Airplane(
                    dispatcher,
                    t_s.id,
                    trajectory_planned=trace,
                    size=5,
                    start_time=t_s.time_start,
                    end_time=t_s.time_finish,
                    vel=np.array([t_s.speed * np.cos(t_s.direction * np.pi/180), t_s.speed * np.sin(t_s.direction * np.pi/180), 0])
                )
            )

        env = AeroEnv(dispatcher, -2, targets=targets)

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
            if r_s.overview_mode == 0:
                configuration.append(RadarRound(dispatcher, r_s.id, cp_source.id, env, np.array([r_s.x, r_s.y, r_s.z]), 
                                                r_s.pan_start, r_s.tilt_start, r_s.view_distance,
                                                r_s.pan_per_sec, r_s.tilt_per_sec))
            else: 
                configuration.append(RadarSector(dispatcher, r_s.id, cp_source.id, env, np.array([r_s.x, r_s.y, r_s.z]), 
                                                 r_s.pan_start, r_s.tilt_start, r_s.view_distance, r_s.pan_angle, r_s.tilt_angle,
                                                 r_s.pan_per_sec, r_s.tilt_per_sec, r_s.type))

        # CP
        configuration.append(CombatControlPoint(dispatcher, cp_source.id, sd_info))
        dispatcher.configurate(configuration)
        return dispatcher

    def startSimulation(self, model_sources):
        self.dispatcher = self.buildModels(model_sources)
        if self.status == STATUS.NO_ERROR:
            self.dispatcher.tick.connect(self.updateProgress)
            self.thread = CustomThread(self.dispatcher.run)
            self.thread.finished.connect(self.onSimulationEnded)
            self.window.setValue(0)
            self.window.setMaximum(floor(model_sources[0].getTime() * 10))
            self.thread.start()
            self.window.exec_()
        else:
            self.onErrorRaised()

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

    def onErrorRaised(self):
        msgBox = QMessageBox()
        if self.status == STATUS.BAD_TRACE_CONFIG:
            msgBox.setText("Неправильная конфигурация трасс воздушных целей. Исправьте, сделав все трассы синими.")
        msgBox.exec()