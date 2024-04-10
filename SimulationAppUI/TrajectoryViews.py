import sys
import traceback

import numpy as np

from PyQt5.QtGui import QPainter, QPen, QBrush
from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtGui import QPainter, QColor, QFont
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QPushButton, QHBoxLayout, QWidget
from PyQt5.QtWidgets import QCheckBox, QHBoxLayout, QWidget, QVBoxLayout, QGraphicsItemGroup

import sys
from PyQt5.QtWidgets import QApplication, QGraphicsView, QGraphicsScene, QGraphicsItem, QMainWindow
from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsTextItem, QGraphicsLineItem
from PyQt5.QtCore import Qt, QPointF, QRectF


class CustomCheckBox(QCheckBox):
    def __init__(self, text, object_id, obj_type):
        super().__init__(text)
        self.simulated_object_id = object_id
        self.obj_type = obj_type


class СhooseViewWidget(QWidget):
    def __init__(self, text, object_id, obj_type):
        super().__init__()
        layout = QHBoxLayout()
        self.checkbox = CustomCheckBox(text, object_id, obj_type)
        layout.addWidget(self.checkbox)
        self.setLayout(layout)
        self.simulated_object_id = object_id
        self.obj_type = obj_type


    def setIcon(self, icon):
        self.checkbox.setIcon(icon)

    def setIconSize(self, size):
        self.checkbox.setIconSize(size)

    def bindFunctionToCheckboxClicked(self, function):
        self.checkbox.stateChanged.connect(function)

    def getValue(self):
        if self.checkbox.isChecked():
            return True
        else:
            return False


class TargetTrajectorySection(QGraphicsItem):
    def __init__(self, point_start, point_end, info):
        super().__init__()
        self.point_start = point_start
        self.point_end = point_end
        self.traj_info = info
        self.setFlags(QGraphicsItem.ItemIsSelectable)

    def boundingRect(self):
        return QRectF(self.point_start[0], self.point_start[1],
                      self.point_end[0] - self.point_start[0], self.point_end[1] - self.point_start[1])

    def paint(self, painter, option, widget):
        pen = QPen(Qt.blue)
        pen.setWidth(6)
        painter.setPen(pen)
        painter.drawLine(self.point_start[0], self.point_start[1], self.point_end[0], self.point_end[1])

    def mousePressEvent(self, event):
        print(f"Traj info: {self.traj_info}")

class MissileTrajectorySection(TargetTrajectorySection):
    def __init__(self, point_start, point_end, info):
        super().__init__(point_start, point_end, info)

    def paint(self, painter, option, widget):
        pen = QPen(Qt.black)
        pen.setWidth(2)
        painter.setPen(pen)
        painter.drawLine(self.point_start[0], self.point_start[1], self.point_end[0], self.point_end[1])

    def mousePressEvent(self, event):
        print(f"Traj info: {self.traj_info}")


class TrajGraphicsView(QGraphicsView):
    def __init__(self, scene):
        super().__init__(scene)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

class TrajGraphicsScene(QGraphicsScene):
    def __init__(self, lines_data=None, parent=None,):
        super().__init__(parent)
        self.setSceneRect(-100, -100, 200, 200)  # Устанавливаем размер сцены
        self.trajectories = None
        self.setLinesData(lines_data)
        self.kx_compression = 500
        self.ky_compression = -500
        self.y_max = 300000
        self.x_max = 300000
        self.add_grid()
        self.add_axis()

    def setLinesData(self, data):
        # if not isinstance(data, dict):
        #     return
        self.trajectories = data

    def updateLinesData(self, clicked_radars, clicked_controls, clicked_vo):
        if not isinstance(self.trajectories, dict):
            return

        print("in update lines data")
        # print(clicked_controls)
        # print(clicked_vo)
        # print(self.trajectories)
        self.clear()
        self.add_grid()
        self.add_axis()

        try:
            for rad_id in clicked_radars:
                obj_trajs = self.trajectories["radars"][rad_id]
                for key, value in obj_trajs.items():
                    obj_id = key
                    obj_traj = value
                    # print("kv", key, value)
                    self.addTraj(obj_traj)

            for control_id in clicked_controls:
                obj_trajs = self.trajectories["controls"][control_id]
                for key, value in obj_trajs.items():
                    obj_id = key
                    obj_traj = value
                    # print("kv", key, value)
                    self.addTraj(obj_traj)

            if clicked_vo:
                #for key in ["targets", "missiles"]:
                obj_trajs = self.trajectories["vo"]["targets"]
                for key, value in obj_trajs.items():
                    obj_id = key
                    obj_traj = value
                    # print("kv for vo", key, len(value))
                    self.addTargetTraj(obj_traj)
                obj_trajs = self.trajectories["vo"]["missiles"]
                for key, value in obj_trajs.items():
                    obj_id = key
                    obj_traj = value
                    # print("kv for vo", key, len(value))
                    self.addMissileTraj(obj_traj)
        except:
            traceback.print_exc()

        self.update()

    def addMissileTraj(self, obj_traj):
        # print(f"Adding missele traj len ={len(obj_traj)}")
        #print(self.coordinates_center)
        traj = obj_traj
        for i in range(1, len(traj)):
            # print(i, len(traj))
            #print(self.coordinates_center, traj[i - 1])
            #point = self.coordinates_center + traj[i]
            #prev_point = self.coordinates_center + traj[i - 1]
            point = [traj[i][0] / self.kx_compression, traj[i][1] / self.ky_compression]
            prev_point = [traj[i - 1][0] / self.kx_compression, traj[i - 1][1] / self.ky_compression]
            # print(point, prev_point)
            line = MissileTrajectorySection(point, prev_point, f"section {i}")
            self.addItem(line)

    def addTargetTraj(self, obj_traj):
        # print(f"Adding target traj len ={len(obj_traj)}")
        traj = obj_traj
        for i in range(1, len(traj)):
            point = [traj[i][0] / self.kx_compression, traj[i][1] / self.ky_compression]
            prev_point = [traj[i - 1][0] / self.kx_compression, traj[i - 1][1] / self.ky_compression]
            line = TargetTrajectorySection(point, prev_point, f"section {i}")
            self.addItem(line)


    def add_axis(self):
        x_axis = QGraphicsLineItem(-self.x_max / self.kx_compression, 0, self.x_max / self.kx_compression, 0)
        x_axis.setPen(Qt.black)
        self.addItem(x_axis)

        step_x = 30000
        for x in range(-self.x_max, self.x_max + 1, step_x):
            text_item = QGraphicsTextItem(str(x))
            text_item.setPos(x / self.kx_compression, -5)
            self.addItem(text_item)

        y_axis = QGraphicsLineItem(0, -self.y_max / self.ky_compression, 0, self.y_max / self.ky_compression)
        y_axis.setPen(Qt.black)
        self.addItem(y_axis)

        step_y = 30000
        for y in range(-self.y_max, self.y_max, step_y):
            if abs(y) < step_y/4:
                continue
            text_item = QGraphicsTextItem(str(y))
            text_item.setPos(1, y / self.ky_compression)
            self.addItem(text_item)

    def add_grid(self):
        grid_group = QGraphicsItemGroup()

        step_x = 30000
        for x in range(-self.x_max, self.x_max + 1, step_x):
            line = QGraphicsLineItem(x / self.kx_compression, -self.y_max / self.ky_compression,
                                     x / self.kx_compression, self.y_max / self.ky_compression)
            line.setPen(Qt.lightGray)
            grid_group.addToGroup(line)

        step_y = 30000
        for y in range(-self.y_max, self.y_max, step_y):
            line = QGraphicsLineItem(-self.x_max / self.kx_compression, y / self.ky_compression,
                                     self.x_max / self.kx_compression, y / self.ky_compression)
            line.setPen(Qt.lightGray)
            grid_group.addToGroup(line)

        self.addItem(grid_group)


class TrajectoryViews(QWidget):
    def __init__(self):
        super().__init__()
        self.vo_clicked = False
        self.clicked_radars = []
        self.clicked_controls = []

        widget_geometry = self.geometry()
        center_x = widget_geometry.x() + widget_geometry.width() / 2
        center_y = widget_geometry.y() + widget_geometry.height() / 2
        self.coordinates_center = np.array([center_x, center_y])

        self.initUI()


    def initUI(self):
        self.view_layout = QVBoxLayout()
        self.scene = TrajGraphicsScene()
        self.view = TrajGraphicsView(self.scene)
        self.setLayout(self.view_layout)
        self.view_layout.addWidget(self.view)

        # self.setGeometry(300, 300, 280, 170)
        self.setWindowTitle('TrajView')
        self.frameColor = QColor(169, 169, 169)
        # self.show()

    def menuVOClicked(self, value):
        self.clicked_vo = value
        self.scene.updateLinesData(self.clicked_radars, self.clicked_controls, self.clicked_vo)

    def menuRadarClicked(self, radar_id : int, value : bool):
        if not value:
            if radar_id in self.clicked_radars:
                self.clicked_radars.remove(radar_id)
        else:
            self.clicked_radars.append(radar_id)

        print(f"List updated: {self.clicked_radars}")
        self.scene.updateLinesData(self.clicked_radars, self.clicked_controls, self.vo_clicked)

    def menuControlClicked(self, control_id : int, value : bool):
        if not value:
            if control_id in self.clicked_controls:
                self.clicked_controls.remove(control_id)
        else:
            self.clicked_controls.append(control_id)

        print(f"List updated: {self.clicked_controls}")
        self.scene.updateLinesData(self.clicked_radars, self.clicked_controls, self.vo_clicked)

    def setTrajectories(self, trajs):
        self.trajectories = trajs
        self.scene.setLinesData(trajs)

    # def paintEvent(self, event):
    #     # qp = QPainter()
    #     #qp.begin(self)
    #     #self.drawFrame(qp)
    #     #print(self.trajectories)
    #     # self.drawAllTrajs(event, qp)
    #     # qp.end()
    #

    # def drawFrame(self, qp):
    #     pen = QPen(self.frameColor)
    #     pen.setWidth(4)
    #     qp.setPen(pen)
    #     qp.drawRect(0, 0, self.width() - 1, self.height() - 1)

    # def drawTraj(self, event, qp, traj, obj_id):
    #     print(f"drawing for obj, id={obj_id}")
    #     qp.setPen(QColor(168, 34, 3))
    #     qp.setFont(QFont('Decorative', 12))
    #
    #     print(self.coordinates_center)
    #     print(traj)
    #     for i in range(1, len(traj)):
    #         print(i, len(traj))
    #         print(self.coordinates_center, traj[i - 1])
    #         point = self.coordinates_center + traj[i]
    #         prev_point = self.coordinates_center + traj[i - 1]
    #         print(point, prev_point)
    #         qp.drawLine(point[0], point[1], prev_point[0], prev_point[1])
    #         qp.drawEllipse(point[0], point[1], 5, 5)
    #         print("drawn")
    #
    #     print("cycle")
    #     qp.setPen(QColor(0, 0, 100))
    #     qp.drawText(self.coordinates_center[0] + traj[-1][0], self.coordinates_center[1] + traj[-1][1], f'TrajExample id={obj_id}')
    #     print("func")





if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = QMainWindow()

    window.setWindowTitle('Clickable Graphics View')
    window.show()
    sys.exit(app.exec_())
