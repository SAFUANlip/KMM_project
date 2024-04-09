import sys

# from ObjectsList import ObjectsList
from PyQt5.QtCore import (pyqtSignal, pyqtSlot)
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QHBoxLayout, QToolBar, QListWidget, QAction)
from PyQt5.QtWidgets import QPushButton, QListWidgetItem

from ConfigureView.ConfiguratingViewport import ConfiguratingViewport
from SimulationModule import SimulationModule
from TrajectoryViews import TrajectoryViews


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

<<<<<<< Updated upstream
        self.pixmaps = {1 : QPixmap(('./images/control_station_icon.png')).scaledToHeight(50),
                2 : QPixmap(('./images/radar_icon.png')).scaledToHeight(50),
                3 : QPixmap(('./images/missile_launcher_icon.png')).scaledToHeight(50),
                4 : QPixmap(('./images/aircraft_icon.png')).scaledToHeight(25)}
=======
        self.pixmaps = {1: QPixmap('./images/control_station_icon.png').scaledToHeight(50),
                        2: QPixmap('./images/radar_icon.png').scaledToHeight(50),
                        3: QPixmap('./images/missile_launcher_icon.png').scaledToHeight(50),
                        4: QPixmap('./images/aircraft_icon.png').scaledToHeight(25)}
>>>>>>> Stashed changes

        # потом перепишем)
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

        action1 = QAction("ConfigureView", self)
        action2 = QAction("TrajView", self)
        action3 = QAction("Настройки моделирования", self)
        action4 = QAction("Начать моделирование", self)

        action1.triggered.connect(self.changeViewConf)
        action1.triggered.connect(lambda: action3.setVisible(True))
        action1.triggered.connect(lambda: action4.setVisible(True))
        action2.triggered.connect(self.changeViewTraj)
        action2.triggered.connect(lambda: action3.setVisible(False))
        action2.triggered.connect(lambda: action4.setVisible(False))
        tool_bar.addAction(action1)
        tool_bar.addAction(action2)
        tool_bar.addAction(action3)
        tool_bar.addAction(action4)

        self.traj_view = False
        self.configure_view = False

        self.simulation_module = SimulationModule(self)
        action4.triggered.connect(self.onSimulationStartRequested)
        self.left_conf_widget = ConfiguratingViewport(self.pixmaps, QApplication.startDragDistance(), parent=self)
        self.sigItemAddRequested.connect(self.left_conf_widget.addItem)
        self.simulation_module.simulationEnded.connect(self.onSimulationEnded)
        action3.triggered.connect(self.left_conf_widget.openModelingSettingsWindow)
        self.layout.addWidget(self.left_conf_widget)

        self.left_traj_widget = TrajectoryViews()
        self.left_traj_widget.hide()
        self.layout.addWidget(self.left_traj_widget)

        self.right_widget = QListWidget()

        # ------ Radar button --------------------------------------------------
        item = QListWidgetItem()
        button = QPushButton(text=f" МФР(дальность 150км)", parent=self)
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
        # item.setSizeHint(button.sizeHint())
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
        # item.setSizeHint(button.sizeHint())
        self.right_widget.addItem(item)
        self.right_widget.setItemWidget(item, button)
        # --------------------------------------------------------------------------

        # ------ Airplane button --------------------------------------------------
        item = QListWidgetItem()
        button = QPushButton(text=f" TС", parent=self)
        button.clicked.connect(self.onListAirplaneClicked)

        button.setFixedHeight(80)
        button.setIcon(QIcon(self.pixmaps[4]))
        button.setIconSize(button.size())

        button.setFixedHeight(100)
        item.setSizeHint(button.size())
        # item.setSizeHint(button.sizeHint())
        self.right_widget.addItem(item)
        self.right_widget.setItemWidget(item, button)
        # --------------------------------------------------------------------------

        self.layout.addWidget(self.right_widget)

        self.layout.setStretchFactor(self.left_conf_widget, 3)
        self.layout.setStretchFactor(self.left_traj_widget, 3)
        self.layout.setStretchFactor(self.right_widget, 1)

        self.setGeometry(100, 100, 1280, 960)

    def changeViewTraj(self):
        action = self.sender()
        if action:
            print("ToolBarButton clicked:", action.text())
        print("Swapping widgets")
        self.left_conf_widget.hide()
        self.right_widget.hide()
        self.left_traj_widget.show()

    def changeViewConf(self):
        action = self.sender()
        if action:
            print("ToolBarButton clicked:", action.text())
        print("Swapping widgets")
        self.left_traj_widget.hide()
        self.left_conf_widget.show()
        self.right_widget.show()

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
    def onSimulationEnded(self, result):
        print('Simulation ended, maybe there should be some code here.')


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
