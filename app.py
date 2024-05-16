import sys
from pathlib import Path

from PyQt5.QtCore import (Qt, pyqtSignal, pyqtSlot)
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QHBoxLayout,
                             QToolBar, QListWidget, QAction, QSlider, QLabel)
from PyQt5.QtWidgets import QPushButton, QListWidgetItem, QSizePolicy

from simulation_app_ui.MessagesParser import parse_messages
from simulation_app_ui.SimulationModule import SimulationModule
from simulation_app_ui.TrajectoryViews import TrajectoryViews, ZoomGraphicsView
from simulation_app_ui.TrajectoryViews import СhooseViewWidget, CustomCheckBox
from simulation_app_ui.configure_view.ConfiguratingViewport import ConfiguratingViewport



class MainWindow(QMainWindow):
    num_items = 15
    sigRadar = pyqtSignal(int)
    sigMissileLauncher = pyqtSignal(int)
    sigControlStation = pyqtSignal(int)
    sigAHelicopter = pyqtSignal(int)
    sigAirplane = pyqtSignal(int)
    sigItemAddRequested = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        head_path = Path.cwd().resolve()

        print(head_path)

        self.pixmaps = {
            1: QPixmap(str(head_path / Path(('simulation_app_ui/images/control_station_icon.png')))).scaledToHeight(50),
            2: QPixmap(str(head_path / Path(('simulation_app_ui/images/radar_icon.png')))).scaledToHeight(50),
            3: QPixmap(str(head_path / Path(('simulation_app_ui/images/missile_launcher_icon.png')))).scaledToHeight(50),
            4: QPixmap(str(head_path / Path(('simulation_app_ui/images/aircraft_icon.png')))).scaledToHeight(25)}

        self.sigRadar.connect(self.sigItemAddRequested)
        self.sigMissileLauncher.connect(self.sigItemAddRequested)
        self.sigControlStation.connect(self.sigItemAddRequested)
        self.sigAHelicopter.connect(self.sigItemAddRequested)
        self.sigAirplane.connect(self.sigItemAddRequested)

        self.initUI()

    def initUI(self):
        self.sigRadar.connect(self.sigAirplaneHandler)
        self.sigMissileLauncher.connect(self.sigAirplaneHandler)
        self.sigControlStation.connect(self.sigAirplaneHandler)
        self.sigAirplane.connect(self.sigAirplaneHandler)

        self.setWindowTitle("SimulationApp")
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        self.layout = QHBoxLayout(main_widget)

        tool_bar = QToolBar("Toolbar", self)
        self.addToolBar(tool_bar)

        action1 = QAction("Отображение конфигурации", self)
        action2 = QAction("Отображение траекторий", self)
        action3 = QAction("Настройки моделирования", self)
        action4 = QAction("Начать моделирование", self)
        action5 = QAction("Сохранить конфигурацию", self)
        action6 = QAction("Загрузить конфигурацию", self)

        self.action_toolbar = lambda: [f for f in [action2.setVisible(False),
                                                   action1.setVisible(True),
                                                   action3.setVisible(False),
                                                   action4.setVisible(False),
                                                   action5.setVisible(False),
                                                   action6.setVisible(False)]]

        action1.triggered.connect(self.changeViewConf)
        action1.triggered.connect(lambda: action3.setVisible(True))
        action1.triggered.connect(lambda: action1.setVisible(False))
        action1.triggered.connect(lambda: action2.setVisible(True))
        action1.triggered.connect(lambda: action4.setVisible(True))
        action1.triggered.connect(lambda: action5.setVisible(True))
        action1.triggered.connect(lambda: action6.setVisible(True))
        action2.triggered.connect(self.changeViewTraj)
        action2.triggered.connect(lambda: action3.setVisible(False))
        action2.triggered.connect(lambda: action1.setVisible(True))
        action2.triggered.connect(lambda: action2.setVisible(False))
        action2.triggered.connect(lambda: action4.setVisible(False))
        action2.triggered.connect(lambda: action5.setVisible(False))
        action2.triggered.connect(lambda: action6.setVisible(False))
        tool_bar.addAction(action1)
        tool_bar.addAction(action2)
        tool_bar.addAction(action5)
        tool_bar.addAction(action6)
        tool_bar.addAction(action3)
        tool_bar.addAction(action4)
        action1.setVisible(False)

        self.traj_view = False
        self.configure_view = False

        self.simulation_module = SimulationModule(self)
        action4.triggered.connect(self.onSimulationStartRequested)
        self.left_conf_widget = ConfiguratingViewport(self.pixmaps, QApplication.startDragDistance(), parent=self)
        self.sigItemAddRequested.connect(self.left_conf_widget.addItem)
        self.simulation_module.simulationEnded.connect(self.onSimulationEnded)
        action3.triggered.connect(self.left_conf_widget.openModelingSettingsWindow)
        action5.triggered.connect(self.left_conf_widget.onConfigurationSaveClicked)
        action6.triggered.connect(self.left_conf_widget.onConfigurationLoadClicked)
        self.layout.addWidget(self.left_conf_widget)

        self.left_traj_widget = TrajectoryViews(pixmaps=self.pixmaps)
        self.left_traj_widget.hide()
        self.layout.addWidget(self.left_traj_widget)

        self.right_widget = QListWidget()

        # ------ Radar button --------------------------------------------------
        item = QListWidgetItem()
        button = QPushButton(text=f" МФР(дальность 50км)", parent=self)
        button.clicked.connect(self.onListRadarClicked)

        button.setFixedHeight(80)
        button.setIcon(QIcon(self.pixmaps[2]))
        button.setIconSize(button.size())

        button.setFixedHeight(100)
        item.setSizeHint(button.size())
        # item.setSizeHint(button.sizeHint())
        self.right_widget.addItem(item)
        self.right_widget.setItemWidget(item, button)
        # --------------------------------------------------------------------------

        # ------ Control Station button --------------------------------------------------
        item = QListWidgetItem()
        button = QPushButton(text=f" ПБУ", parent=self)
        button.clicked.connect(self.onListControlStationClicked)

        button.setFixedHeight(80)
        button.setIcon(QIcon(self.pixmaps[1]))
        button.setIconSize(button.size())

        button.setFixedHeight(100)
        item.setSizeHint(button.size())
        self.right_widget.addItem(item)
        self.right_widget.setItemWidget(item, button)
        # --------------------------------------------------------------------------

        # ------ Missile Launcher button --------------------------------------------------
        item = QListWidgetItem()
        button = QPushButton(text=f" ПУ", parent=self)
        button.clicked.connect(self.onListMissileLauncherClicked)

        button.setFixedHeight(80)
        button.setIcon(QIcon(self.pixmaps[3]))
        button.setIconSize(button.size())

        button.setFixedHeight(100)
        item.setSizeHint(button.size())
        self.right_widget.addItem(item)
        self.right_widget.setItemWidget(item, button)
        # --------------------------------------------------------------------------

        # ------ Airplane button --------------------------------------------------
        item = QListWidgetItem()
        button = QPushButton(text=f" Самолет", parent=self)
        button.clicked.connect(self.onListAirplaneClicked)

        button.setFixedHeight(80)
        button.setIcon(QIcon(self.pixmaps[4]))
        button.setIconSize(button.size())

        button.setFixedHeight(100)
        item.setSizeHint(button.size())
        self.right_widget.addItem(item)
        self.right_widget.setItemWidget(item, button)
        # --------------------------------------------------------------------------
        self.layout.addWidget(self.right_widget)

        self.choose_views_list = QListWidget()
        self.choose_views_list.hide()
        self.layout.addWidget(self.choose_views_list)

        self.layout.setStretchFactor(self.left_conf_widget, 3)
        self.layout.setStretchFactor(self.left_traj_widget, 3)
        self.layout.setStretchFactor(self.right_widget, 1)
        self.layout.setStretchFactor(self.choose_views_list, 1)

        self.setGeometry(100, 100, 1280, 960)

    def handleCheckboxStateChanged(self, state):
        if state == 2:  # Qt.Checked
            print(f"Checkbox '{self.checkbox.text()}' is checked")
        else:
            print(f"Checkbox '{self.checkbox.text()}' is unchecked")

    def changeViewTraj(self):
        action = self.sender()
        if action:
            print("ToolBarButton clicked:", action.text())
        print("Swapping widgets")
        self.setViewTraj()

    def changeViewConf(self):
        action = self.sender()
        if action:
            print("ToolBarButton clicked:", action.text())
        print("Swapping widgets")
        self.left_traj_widget.clearAll()
        self.left_traj_widget.hide()
        self.choose_views_list.hide()
        self.left_conf_widget.show()
        self.right_widget.show()

    def setViewTraj(self):
        self.left_conf_widget.hide()
        self.right_widget.hide()
        self.left_traj_widget.show()
        self.choose_views_list.show()

    def onListRadarClicked(self):
        button = self.sender()
        if button:
            print("List item button clicked:", button.text())

        # change STR on necessary INT
        self.sigControlStation.emit(2001)
        print("Signal emitted", button.text())

    def onListControlStationClicked(self):
        button = self.sender()
        if button:
            print("List item button clicked:", button.text())

        # change STR on necessary INT
        self.sigControlStation.emit(1001)
        print("Signal emitted", button.text())

    def onListMissileLauncherClicked(self):
        button = self.sender()
        if button:
            print("List item button clicked:", button.text())

        # change STR on necessary INT
        self.sigMissileLauncher.emit(3001)
        print("Signal emitted", button.text())

    def onListAirplaneClicked(self):
        button = self.sender()
        if button:
            print("List item button clicked:", button.text())

        # change STR on necessary INT
        self.sigAirplane.emit(4001)
        print("Signal emitted", button.text())

    def sigRadarHandler(self, arg):
        print("Handler:", arg)

    def sigConstrolStationHandler(self, arg):
        print("Handler:", arg)

    def sigAMisseleLauncherHandler(self, arg):
        print("Handler:", arg)

    def sigAirplaneHandler(self, arg):
        print("Handler:", arg)

    @pyqtSlot()
    def onSimulationStartRequested(self):
        self.simulation_module.startSimulation(self.left_conf_widget.getModelSources())

    @pyqtSlot(object)
    def onSimulationEnded(self, all_messages):
        print('Simulation ended, got messages to parse.')

        # parse messages
        objs, trajs = parse_messages(all_messages)
        # load configured data of radars and controls
        conf_items = self.left_conf_widget.models
        self.configure_choosing_view_widgets(objs, trajs, conf_items)

        self.setViewTraj()
        self.action_toolbar()

    def configure_choosing_view_widgets(self, obj_viewing: dict[str, list[int]], obj_trajs,
                                        conf_items):  #: dict[str, dict(int, dict(int,list[np.array])):
        self.choose_views_list.clear()
        self.left_traj_widget.setTrajectories(obj_trajs)
        filtered_items = conf_items[1:]
        self.left_traj_widget.setConfItems(filtered_items)

        max_time = obj_trajs["max_time"]

        item_height = 45

        item = QListWidgetItem()
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(0)
        self.slider.setMaximum(int(max_time))
        self.slider.setValue(int(max_time))
        self.slider.setTickInterval(int(max_time / 10))
        self.slider.setTickPosition(QSlider.TicksBelow)
        self.slider.setFixedHeight(item_height)
        self.slider.sliderReleased.connect(self.sliderTimeReleased)
        self.slider.sliderPressed.connect(self.sliderTimeReleased)
        self.slider.valueChanged.connect(self.sliderTimeValueMoving)
        self.slider.valueChanged.connect(self.sliderTimeReleased)

        item.setSizeHint(self.slider.sizeHint())
        self.choose_views_list.addItem(item)
        self.choose_views_list.setItemWidget(item, self.slider)

        item = QListWidgetItem()
        self.label_slider_value = QLabel(f"Время: {str(self.slider.value())} сек")
        self.label_slider_value.setFixedHeight(item_height)
        item.setSizeHint(self.label_slider_value.sizeHint())
        self.choose_views_list.addItem(item)
        self.choose_views_list.setItemWidget(item, self.label_slider_value)

        item = QListWidgetItem()
        widget = СhooseViewWidget(f"BO", 0, "vo")
        widget.setFixedHeight(item_height)
        widget.bindFunctionToCheckboxClicked(self.onChooseViewItemClicked)
        item.setSizeHint(widget.sizeHint())
        self.choose_views_list.addItem(item)
        self.choose_views_list.setItemWidget(item, widget)

        for radar_id in obj_viewing["radars"]:
            item = QListWidgetItem()
            widget = СhooseViewWidget(f"МФР {radar_id}", radar_id, "radar")
            widget.bindFunctionToCheckboxClicked(self.onChooseViewItemClicked)
            widget.setFixedHeight(item_height)
            widget.setIcon(QIcon(self.pixmaps[2]))
            item.setSizeHint(widget.sizeHint())
            self.choose_views_list.addItem(item)
            self.choose_views_list.setItemWidget(item, widget)

        for control_id in obj_viewing["controls"]:
            item = QListWidgetItem()
            widget = СhooseViewWidget(f"ПБУ {control_id}", control_id, "control")
            widget.bindFunctionToCheckboxClicked(self.onChooseViewItemClicked)
            widget.setFixedHeight(item_height)
            widget.setIcon(QIcon(self.pixmaps[1]))
            item.setSizeHint(widget.sizeHint())
            self.choose_views_list.addItem(item)
            self.choose_views_list.setItemWidget(item, widget)

        item = QListWidgetItem()
        zoom_view = ZoomGraphicsView(self.left_traj_widget.scene)
        zoom_view.show()
        zoom_view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        zoom_view.setFixedHeight(450)
        self.choose_views_list.addItem(item)
        self.choose_views_list.setItemWidget(item, zoom_view)

    def sliderTimeValueMoving(self, value):
        self.label_slider_value.setText(f"Время: {value} сек")

    def sliderTimeReleased(self):
        value = self.slider.value()
        self.left_traj_widget.updateChosenTime(value)

    def onChooseViewItemClicked(self):
        item = self.sender()
     
        if not isinstance(item, CustomCheckBox):
            return

        if item.obj_type == "radar":
            self.left_traj_widget.menuRadarClicked(item.simulated_object_id, item.isChecked())
        elif item.obj_type == "control":
            self.left_traj_widget.menuControlClicked(item.simulated_object_id, item.isChecked())
        elif item.obj_type == "vo":
            self.left_traj_widget.menuVOClicked(item.isChecked())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
