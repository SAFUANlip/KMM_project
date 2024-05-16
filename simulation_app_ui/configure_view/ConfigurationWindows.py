from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QHBoxLayout, QVBoxLayout, QSpinBox, QComboBox, QFormLayout
from src.constants import Airplane_SPEED_MIN, Airplane_SPEED_MAX, env_limits, min_model_time, max_model_time


class DispatcherConfigWindow(QDialog):
    def __init__(self, parent=None):
        super(DispatcherConfigWindow, self).__init__(parent)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setWindowTitle("Настройки моделирования")
        self.fields = {}
        base_layout = QVBoxLayout()
        form_layout = QFormLayout()
        spinbox = QSpinBox()
        spinbox.setButtonSymbols(QSpinBox.NoButtons)
        spinbox.setRange(min_model_time, max_model_time)
        form_layout.addRow("Время моделирования: с", spinbox)
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
        for label_name in env_limits:
            form_layout = QFormLayout()
            spinbox = QSpinBox()
            spinbox.setButtonSymbols(QSpinBox.NoButtons)
            spinbox.setRange(env_limits[label_name][0], env_limits[label_name][1])
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
        form_layout.addRow('Начальный сектор: °', spinbox)
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
        form_layout.addRow('Угол раскрыва по азимуту: °', spinbox)
        self.fields['pan_angle'] = spinbox
        spinbox.setEnabled(False)

        layout.addLayout(form_layout)
        base_layout.addLayout(layout)
        self.setLayout(base_layout)


class StartDeviceWindow(PosConfigWindow):
    def __init__(self, parent=None):
        super(StartDeviceWindow, self).__init__(parent)
        self.setWindowTitle("Свойства пусковой установки")


class AeroTargetWindow(PosConfigWindow):
    def __init__(self, parent=None):
        super(AeroTargetWindow, self).__init__(parent)
        self.setWindowTitle("Свойства Цели")

        base_layout = self.layout()

        layout = QHBoxLayout()
        form_layout = QFormLayout()

        spinbox = QSpinBox()
        spinbox.setButtonSymbols(QSpinBox.NoButtons)
        spinbox.setRange(Airplane_SPEED_MIN, Airplane_SPEED_MAX)
        form_layout.addRow('Скорость: м/с', spinbox)
        self.fields['V'] = spinbox

        spinbox = QSpinBox()
        spinbox.setButtonSymbols(QSpinBox.NoButtons)
        spinbox.setRange(0, max_model_time//2)
        form_layout.addRow('Время начала: с', spinbox)
        self.fields['t_start'] = spinbox

        layout.addLayout(form_layout)

        form_layout = QFormLayout()

        spinbox = QSpinBox()
        spinbox.setButtonSymbols(QSpinBox.NoButtons)
        spinbox.setRange(-360, 360)
        form_layout.addRow('Курс: °', spinbox)
        self.fields['direction'] = spinbox

        spinbox = QSpinBox()
        spinbox.setButtonSymbols(QSpinBox.NoButtons)
        spinbox.setRange(max_model_time//2, max_model_time)
        form_layout.addRow('Время окончания: с', spinbox)
        self.fields['t_finish'] = spinbox

        layout.addLayout(form_layout)

        base_layout.addLayout(layout)
        self.setLayout(base_layout)


class TrackPointWindow(PosConfigWindow):
    def __init__(self, parent=None):
        super(TrackPointWindow, self).__init__(parent)
        self.setWindowTitle("Свойства точки траектории")
