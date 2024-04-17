from PyQt5.QtCore import QObject
from PyQt5.QtCore import pyqtSignal

class DispatcherSource:
    def __init__(self):
        self.time = 250

    def setTime(self, time):
        self.time = time

    def getTime(self):
        return self.time

class BaseSource(QObject):

    dataChanged = pyqtSignal()

    def __init__(self, id, model_type, x, y):
        super(BaseSource, self).__init__()
        self.id = id
        self.model_type = model_type
        self.x = x
        self.y = y
        self.z = 0
        self.is_movement_notifying = False

    def setX(self, x):
        self.x = x
        if self.is_movement_notifying:
            self.dataChanged.emit()
    def setY(self, y):
        self.y = y
        if self.is_movement_notifying:
            self.dataChanged.emit()
    def setZ(self, z):
        self.z = z
        if self.is_movement_notifying:
            self.dataChanged.emit()

    def getX(self):
        return self.x
    def getY(self):
        return self.y
    def getZ(self):
        return self.z


class ControlPointSource(BaseSource):
    def __init__(self, id, model_type, x, y):
        super(ControlPointSource, self).__init__(id, model_type, x, y)


class RadarSource(BaseSource):
    def __init__(self, id, model_type, x, y):
        super(RadarSource, self).__init__(id, model_type, x, y)
        self.overview_mode = 0
        self.pan_start = 0
        self.tilt_start = 0
        self.pan_per_sec = 60
        self.tilt_per_sec = 120
        self.view_distance = 150000
        self.type = 'horizontal'
        self.pan_angle = self.pan_per_sec
        self.tilt_angle = self.tilt_per_sec

    def setOverviewMode(self, overview_mode):
        self.overview_mode = overview_mode
        self.dataChanged.emit()
    def setPanStart(self, pan_start):
        self.pan_start = pan_start
        self.dataChanged.emit()
    def setPanAngle(self, pan_angle):
        self.pan_angle = pan_angle
        self.dataChanged.emit()
    def setSectorType(self, type):
        self.type = type

    def getOverviewMode(self):
        return self.overview_mode
    def getPanStart(self):
        return self.pan_start
    def getPanAngle(self):
        return self.pan_angle
    def getSectorType(self):
        return self.type

class StartDeviceSource(BaseSource):
    def __init__(self, id, model_type, x, y):
        super(StartDeviceSource, self).__init__(id, model_type, x, y)


class AeroTargetSource(BaseSource):
    def __init__(self, id, model_type, x, y):
        super(AeroTargetSource, self).__init__(id, model_type, x, y)
        self.z = 10000
        self.speed = 150
        self.direction = 0
        self.time_start = 0
        self.time_finish = 100

    def setSpeed(self, speed):
        self.speed = speed
        self.dataChanged.emit()
    def setDirection(self, direction):
        self.direction = direction
        self.dataChanged.emit()
    def setTimeStart(self, time_start):
        self.time_start = time_start
        self.dataChanged.emit()
    def setTimeFinish(self, time_finish):
        self.time_finish = time_finish
        self.dataChanged.emit()

    def getSpeed(self):
        return self.speed
    def getDirection(self):
        return self.direction
    def getTimeStart(self):
        return self.time_start
    def getTimeFinish(self):
        return self.time_finish

