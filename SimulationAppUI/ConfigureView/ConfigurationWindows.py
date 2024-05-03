from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QHBoxLayout, QVBoxLayout, QSpinBox, QDoubleSpinBox, QComboBox, QFormLayout
from config.constants import Airplane_SPEED_MIN, Airplane_SPEED_MAX


h_max_abs_coord = 100000
v_max_abs_coord = 20000

class DispatcherConfigWindow(QDialog):
    def __init__(self, parent=None):
        super(DispatcherConfigWindow, self).__init__(parent)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setWindowTitle("Настройки моделирования")
        self.fields = {}
        base_layout = QVBoxLayout()
        form_layout = QFormLayout()
        spinbox = QDoubleSpinBox()
        spinbox.setButtonSymbols(QDoubleSpinBox.NoButtons)
        spinbox.setRange(5, 3600*4)
        form_layout.addRow("Время моделирования", spinbox)
        self.fields['sim_time'] = spinbox
        base_layout.addLayout(form_layout)
        self.setLayout(base_layout)


class PosConfigWindow(QDialog):
    def __init__(self, parent=None):
        super(PosConfigWindow, self).__init__(parent)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.fields = {}

        base_layout = QVBoxLayout()
        layout = QHBoxLayout()
        for label_name in ('X: м', 'Y: м', 'Z: м'):
            form_layout = QFormLayout()
            spinbox = QDoubleSpinBox()
            spinbox.setButtonSymbols(QDoubleSpinBox.NoButtons)
            spinbox.setRange(-h_max_abs_coord, h_max_abs_coord)
            form_layout.addRow(label_name, spinbox)
            layout.addLayout(form_layout)
            self.fields[label_name[0]] = spinbox

        base_layout.addLayout(layout)
        self.setLayout(base_layout)


class ControlPointWindow(PosConfigWindow):
    def __init__(self, parent=None):
        super(ControlPointWindow, self).__init__(parent)
        self.setWindowTitle("Свойства пункта боевого управления")


class RadarWindow(PosConfigWindow):
    def __init__(self, parent=None):
        super(RadarWindow, self).__init__(parent)
        self.setWindowTitle("Свойства локатора")

        base_layout = self.layout()

        layout = QHBoxLayout()
        form_layout = QFormLayout()

        spinbox = QSpinBox()
        spinbox.setButtonSymbols(QSpinBox.NoButtons)
        spinbox.setRange(-360, 360)
        form_layout.addRow('Начальный сектор:', spinbox)
        self.fields['pan_start'] = spinbox

        combobox = QComboBox()
        combobox.addItem('Круговой')
        combobox.addItem('Секторный')
        combobox.setCurrentIndex(0)
        form_layout.addRow('Режим обзора:', combobox)
        self.fields['overview'] = combobox

        combobox = QComboBox()
        combobox.addItem('Горизонтальный')
        combobox.addItem('Вертикальный')
        combobox.setCurrentIndex(0)
        form_layout.addRow('Тип секторного обзора:', combobox)
        self.fields['type'] = combobox
        combobox.setEnabled(False)

        spinbox = QSpinBox()
        spinbox.setButtonSymbols(QSpinBox.NoButtons)
        spinbox.setRange(0, 360)
        form_layout.addRow('Угол раскрыва по азимуту:', spinbox)
        self.fields['pan_angle'] = spinbox
        spinbox.setEnabled(False)

        layout.addLayout(form_layout)
        base_layout.addLayout(layout)
        self.setLayout(base_layout)


class StartDeviceWindow(PosConfigWindow):
    def __init__(self, parent = None):
        super(StartDeviceWindow, self).__init__(parent)
        self.setWindowTitle("Свойства пусковой установки")


class AeroTargetWindow(PosConfigWindow):
    def __init__(self, parent=None):
        super(AeroTargetWindow, self).__init__(parent)
        self.setWindowTitle("Свойства Цели")

        base_layout = self.layout()
        
        layout = QHBoxLayout()
        form_layout = QFormLayout()

        spinbox = QDoubleSpinBox()
        spinbox.setButtonSymbols(QDoubleSpinBox.NoButtons)
        spinbox.setRange(Airplane_SPEED_MIN, Airplane_SPEED_MAX)
        form_layout.addRow('Скорость:', spinbox)
        self.fields['V'] = spinbox

        spinbox = QDoubleSpinBox()
        spinbox.setButtonSymbols(QDoubleSpinBox.NoButtons)
        spinbox.setRange(0, 3600)
        form_layout.addRow('Время начала:', spinbox)
        self.fields['t_start'] = spinbox

        layout.addLayout(form_layout)

        form_layout = QFormLayout()

        spinbox = QDoubleSpinBox()
        spinbox.setButtonSymbols(QDoubleSpinBox.NoButtons)
        spinbox.setRange(-360, 360)
        form_layout.addRow('Курс:', spinbox)
        self.fields['direction'] = spinbox

        spinbox = QDoubleSpinBox()
        spinbox.setButtonSymbols(QDoubleSpinBox.NoButtons)
        spinbox.setRange(0, 3600)
        form_layout.addRow('Время окончания:', spinbox)
        self.fields['t_finish'] = spinbox

        layout.addLayout(form_layout)

        base_layout.addLayout(layout)
        self.setLayout(base_layout)


class TrackPointWindow(PosConfigWindow):
    def __init__(self, parent=None):
        super(TrackPointWindow, self).__init__(parent)
        self.setWindowTitle("Свойства точки траектории")
