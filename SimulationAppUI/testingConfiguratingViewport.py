from PyQt5.QtWidgets import QApplication
import sys
import pathlib
from PyQt5.QtGui import QPixmap
from ConfigureView.ConfiguratingViewport import ConfiguratingViewport

if __name__ == '__main__':
    app = QApplication(sys.argv)
    pixmaps = {1 : QPixmap(str(pathlib.Path().resolve() / 'SimulationAppUI/images/control_station_icon.png')).scaledToHeight(75), 
               2 : QPixmap(str(pathlib.Path().resolve() / 'SimulationAppUI/images/radar_icon.png')).scaledToHeight(75),
               3 : QPixmap(str(pathlib.Path().resolve() / 'SimulationAppUI/images/missile_launcher_icon.png')).scaledToHeight(75),
               4 : QPixmap(str(pathlib.Path().resolve() / 'SimulationAppUI/images/aircraft_icon.png')).scaledToHeight(50)}

    viewport = ConfiguratingViewport(pixmaps, QApplication.startDragDistance())
    viewport.addItem(1000, 100, 100)
    viewport.addItem(2000, 200, 300)
    viewport.addItem(2000, 500, 600)
    viewport.addItem(3000, 200, 500)
    viewport.addItem(4000, 650, 150)
    sys.exit(app.exec_())