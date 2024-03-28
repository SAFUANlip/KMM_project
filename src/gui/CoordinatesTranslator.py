from PyQt5.QtCore import QObject, pyqtSignal

class CoordinatesTranslator(QObject):

    scaleChanged = pyqtSignal()

    def __init__(self, widget_hw, widget_hh, world_hw, world_hh):
        super(CoordinatesTranslator, self).__init__()
        self.widget_hw = widget_hw
        self.widget_hh = widget_hh
        self.world_hw = world_hw
        self.world_hh = world_hh

    def translateScreen2World(self, x, y):
        w_x = (x  - self.widget_hw) * self.world_hw / self.widget_hw
        w_y = -(y - self.widget_hh) * self.world_hh/ self.widget_hh
        return w_x, w_y

    def translateWorld2Screen(self, x, y):
        s_x = int(x * self.widget_hw / self.world_hw + self.widget_hw)
        s_y = int(-y * self.widget_hh/ self.world_hh + self.widget_hh)
        return s_x, s_y

    def setNewWidgetSize(self, new_widget_hw, new_widget_hh):
        self.widget_hw = new_widget_hw
        self.widget_hh = new_widget_hh
        self.scaleChanged.emit()