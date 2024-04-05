from PyQt5.QtCore import QObject, pyqtSlot

class DispatcherConfigPresenter(QObject):
    def __init__(self, widget, dispatcher, parent=None):
        super(DispatcherConfigPresenter, self).__init__(parent)
        self.dispatcher = dispatcher
        self.widget = widget
        self.widget.fields['sim_time'].editingFinished.connect(self.updateModelData)
        self.widget.fields['sim_time'].setValue(self.dispatcher.getTime())

    def updateModelData(self):
        self.dispatcher.setTime(self.widget.fields['sim_time'].value())

    def configurate(self):
        self.widget.exec_()


class PosConfigPresenter(QObject):
    def __init__(self, widget, parent=None):
        super(PosConfigPresenter, self).__init__(parent)
        self.widget = widget
        self.widget.fields['X'].editingFinished.connect(self.updateModelData)
        self.widget.fields['Y'].editingFinished.connect(self.updateModelData)
        self.widget.fields['Z'].editingFinished.connect(self.updateModelData)

        self.model = None

    def updateUIFields(self):
        self.widget.fields['X'].setValue(self.model.getX())
        self.widget.fields['Y'].setValue(self.model.getY())
        self.widget.fields['Z'].setValue(self.model.getZ())

    @pyqtSlot()
    def updateModelData(self):
        if self.model:
            self.model.setX(self.widget.fields['X'].value())
            self.model.setY(self.widget.fields['Y'].value())
            self.model.setZ(self.widget.fields['Z'].value())

    def configurate(self, model):
        self.model = model
        self.model.is_movement_notifying = True
        self.updateUIFields()
        self.widget.exec_()
        self.model.is_movement_notifying = False
        self.model = None


class RadarConfigPresenter(PosConfigPresenter):
    def __init__(self, widget, parent=None):
        super(RadarConfigPresenter, self).__init__(widget, parent)
        self.widget.fields['pan_start'].editingFinished.connect(self.updateModelData)
        self.widget.fields['overview'].activated.connect(self.updateModelData)

    def updateUIFields(self):
        super().updateUIFields()
        self.widget.fields['pan_start'].setValue(self.model.getPanStart())
        self.widget.fields['overview'].setCurrentIndex(self.model.getOverviewMode())

    @pyqtSlot()
    def updateModelData(self):
        super().updateModelData()
        if self.model:
            self.model.setPanStart(self.widget.fields['pan_start'].value())
            self.model.setOverviewMode(self.widget.fields['overview'].currentIndex())


class AeroTargetConfigPresenter(PosConfigPresenter):
    def __init__(self, widget, parent=None):
        super(AeroTargetConfigPresenter, self).__init__(widget, parent)
        self.widget.fields['V'].editingFinished.connect(self.updateModelData)
        self.widget.fields['t_start'].editingFinished.connect(self.updateModelData)
        self.widget.fields['direction'].editingFinished.connect(self.updateModelData)
        self.widget.fields['t_finish'].editingFinished.connect(self.updateModelData)

    def updateUIFields(self):
        super().updateUIFields()
        self.widget.fields['V'].setValue(self.model.getSpeed())
        self.widget.fields['t_start'].setValue(self.model.getTimeStart())
        self.widget.fields['direction'].setValue(self.model.getDirection())
        self.widget.fields['t_finish'].setValue(self.model.getTimeFinish())

    @pyqtSlot()
    def updateModelData(self):
        super().updateModelData()
        if self.model:
            self.model.setSpeed(self.widget.fields['V'].value())
            self.model.setTimeStart(self.widget.fields['t_start'].value())
            self.model.setDirection(self.widget.fields['direction'].value())
            self.model.setTimeFinish(self.widget.fields['t_finish'].value())