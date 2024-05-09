import sys
import traceback

import numpy as np

from PyQt5.QtGui import QPainter, QPen, QBrush
from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtGui import QPainter, QColor, QFont, QPainterPath
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QPushButton, QHBoxLayout, QWidget
from PyQt5.QtWidgets import (QCheckBox, QHBoxLayout, QWidget, QVBoxLayout, QGraphicsItemGroup,
                             QGraphicsSimpleTextItem, QGraphicsRectItem,  QGraphicsEllipseItem,
                             QGraphicsPathItem, QGraphicsPixmapItem)

import sys
from PyQt5.QtWidgets import QApplication, QGraphicsView, QGraphicsScene, QGraphicsItem, QMainWindow
from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsTextItem, QGraphicsLineItem
from PyQt5.QtWidgets import QApplication,  QGraphicsEllipseItem
from PyQt5.QtCore import Qt, QPointF, QRectF


from SimulationAppUI.ConfigureView.Models import RadarSource


def filter_sorted_traj(traj, time):
    res = []
    for el in traj:
        if el[3] > time:
            break
        res.append(el)
    return res


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


class TargetPoint(QGraphicsItem):
    def __init__(self, point_pos, radius, color=Qt.blue):
        super().__init__()
        self.point_pos = point_pos
        self.radius = radius
        self.color = color

    def paint(self, painter, option, widget):
        pen = QPen(self.color)
        pen.setWidth(2)
        painter.setPen(pen)
        painter.drawEllipse(int(self.point_pos[0]), int(self.point_pos[1]),
                            int(self.radius), int(self.radius))

    def boundingRect(self):
        return QRectF(self.point_pos[0] - self.radius // 2, self.point_pos[1] - self.radius // 2,
                      self.point_pos[0] + self.radius // 2, self.point_pos[1] + self.radius // 2)

class TargetTrajectorySection(QGraphicsItem):
    def __init__(self, point_start, point_end, info):
        super().__init__()
        self.point_start = point_start
        self.point_end = point_end
        self.traj_info = info
        self.setFlags(QGraphicsItem.ItemIsSelectable)

    def boundingRect(self):
        padding = 2
        return QRectF(self.point_start[0] - padding, self.point_start[1] - padding,
                      self.point_end[0] - self.point_start[0] + padding, self.point_end[1] - self.point_start[1] + padding)

    def paint(self, painter, option, widget):
        pen = QPen(Qt.blue)
        pen.setWidth(4)
        painter.setPen(pen)
        painter.drawLine(int(self.point_start[0]), int(self.point_start[1]),
                         int(self.point_end[0]), int(self.point_end[1]))

    def mousePressEvent(self, event):
        print(f"Traj info: {self.traj_info}")
        scene = self.scene()  # Получаем сцену из родительского виджета
        if scene:
            if scene.traj_info_widget:
                try:
                    scene.removeItem(scene.traj_info_widget)
                    scene.removeItem(scene.traj_info_widget_rect)
                except:
                    print("TrajViews: error removing prev traj-info-text-rect")

            text = f"Traj info: {self.traj_info}"

            # Создаем текстовый элемент
            text_item = QGraphicsTextItem(text)
            text_item.setPos(event.scenePos().x() + 10, event.scenePos().y() + 10)

            # Получаем прямоугольник, охватывающий текст
            text_rect = text_item.boundingRect()
            # Создаем прямоугольник с рамкой на основе размеров текста
            rect = QGraphicsRectItem(QRectF(text_rect.x(), text_rect.y(), text_rect.width(), text_rect.height()))
            rect.setPen(QPen(Qt.black))  # Устанавливаем цвет рамки
            #rect.setBrush(Qt.NoBrush)  # Устанавливаем прозрачную заливку
            rect.setBrush(Qt.white)

            scene.traj_info_widget = text_item #QGraphicsTextItem(text)
            scene.traj_info_widget_rect = rect
            scene.traj_info_widget.setPos(event.scenePos().x() + 10, event.scenePos().y() + 10)
            scene.traj_info_widget_rect.setPos(event.scenePos().x() + 10, event.scenePos().y() + 10)
            scene.addItem(scene.traj_info_widget_rect)  # Добавляем рамку
            scene.addItem(scene.traj_info_widget)  # Добавляем текстовый элемент в сцену
            # rect.addToGroup(text_item)

class MissileTrajectorySection(TargetTrajectorySection):
    def __init__(self, point_start, point_end, info):
        super().__init__(point_start, point_end, info)

    def paint(self, painter, option, widget):
        pen = QPen(Qt.black)
        pen.setWidth(1)
        painter.setPen(pen)
        painter.drawLine(int(self.point_start[0]), int(self.point_start[1]),
                         int(self.point_end[0]), int(self.point_end[1]))



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
        self.kx_compression = 215
        self.ky_compression = -215
        self.y_max = 100000
        self.x_max = 100000
        self.add_grid()
        self.add_axis()
        self.traj_info_widget = QGraphicsTextItem(f"")
        self.traj_info_widget_rect = QGraphicsTextItem(f"")
        self.chosen_time = 0
        self.collected_items = []

    def setLinesData(self, data):
        # if not isinstance(data, dict):
        #     return
        self.trajectories = data

    def updateLinesData(self, clicked_radars, clicked_controls, clicked_vo, chosen_time=None):
        if not isinstance(self.trajectories, dict):
            return

        self.chosen_time = chosen_time

        # print("updating lines data")
        # print(clicked_controls)
        # print(clicked_vo)
        # print(self.trajectories)
        self.clear()
        self.add_grid()
        self.add_axis()
        self.renderCollectedItems()

        try:
            for rad_id in clicked_radars:
                traj = self.trajectories["radars"][rad_id]["targets"]
                obj_points = filter_sorted_traj(traj, self.chosen_time)
                self.addTargetPoints(obj_points, Qt.green)

            for control_id in clicked_controls:
                traj = self.trajectories["controls"][control_id]["targets"]
                obj_points = filter_sorted_traj(traj, self.chosen_time)
                self.addTargetPoints(obj_points)
                obj_trajs = self.trajectories["controls"][control_id]["missiles"]
                for key, value in obj_trajs.items():
                    obj_id = key
                    obj_traj = value
                    # print("kv for vo", key, len(value))
                    obj_traj = filter_sorted_traj(obj_traj, self.chosen_time)
                    self.addMissileTraj(obj_traj)

            if clicked_vo:
                #for key in ["targets", "missiles"]:
                obj_trajs = self.trajectories["vo"]["targets"]
                for key, value in obj_trajs.items():
                    obj_id = key
                    obj_traj = value
                    # print("kv for vo", key, len(value))
                    obj_traj = filter_sorted_traj(obj_traj, self.chosen_time)
                    self.addTargetTraj(obj_traj)
                obj_trajs = self.trajectories["vo"]["missiles"]
                for key, value in obj_trajs.items():
                    obj_id = key
                    obj_traj = value
                    # print("kv for vo", key, len(value))
                    obj_traj = filter_sorted_traj(obj_traj, self.chosen_time)
                    self.addMissileTraj(obj_traj)
        except:
            traceback.print_exc()

        self.update()

    def addMissileTraj(self, obj_traj):
        # print(f"Adding missele traj len ={len(obj_traj)}")
        #print(self.coordinates_center)
        traj = obj_traj
        for i in range(1, len(traj)):
            # time = traj[i][3]
            #
            # if time > self.chosen_time:
            #     break

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

    def addTargetPoints(self, obj_traj, color=Qt.blue):
        # print(f"Adding target traj len ={len(obj_traj)}")
        traj = obj_traj
        for i in range(len(traj)):
            point = [traj[i][0] / self.kx_compression, traj[i][1] / self.ky_compression]
            # prev_point = [traj[i - 1][0] / self.kx_compression, traj[i - 1][1] / self.ky_compression]
            point = TargetPoint(point, 2, color)
            self.addItem(point)

    def addCollectedItem(self, item):
        self.collected_items.append(item)

    def renderCollectedItems(self):
        for item_pair in self.collected_items:
            item = item_pair[0]
            x, y = int(item.x / self.kx_compression), int(item.y / self.ky_compression)
            if isinstance(item, RadarSource):
                view_dist_x = item.view_distance / self.kx_compression
                view_dist_y = item.view_distance / self.ky_compression
                center_x, center_y = x - view_dist_x, y - view_dist_y
                if item.getOverviewMode() == 0:
                    ellipse_item = QGraphicsEllipseItem()
                    ellipse_item.setRect(center_x, center_y, 2 * view_dist_x, 2 * view_dist_y)
                    brush = QBrush(QColor(0, 255, 0, 18))
                    ellipse_item.setBrush(brush)
                    self.addItem(ellipse_item)
                elif item.getOverviewMode() == 1:
                    angle = item.pan_angle
                    start_angle = -item.pan_start - angle
                    path = QPainterPath()
                    path.moveTo(center_x + view_dist_x, center_y + view_dist_y)
                    path.arcTo(center_x, center_y, 2 * view_dist_x, 2 * view_dist_y, start_angle, angle)
                    path.lineTo(center_x + view_dist_x, center_y + view_dist_y)
                    sector_item = QGraphicsPathItem(path)
                    brush = QBrush(QColor(0, 255, 0, 18))
                    sector_item.setBrush(brush)
                    self.addItem(sector_item)

            pixmap = item_pair[1]
            pixmap_item = QGraphicsPixmapItem(pixmap)
            center_x, center_y = x - pixmap.width() / 2, y - pixmap.height() / 2
            pixmap_item.setPos(center_x, center_y)
            self.addItem(pixmap_item)

    def add_axis(self):
        x_axis = QGraphicsLineItem(-self.x_max / self.kx_compression, 0, self.x_max / self.kx_compression, 0)
        x_axis.setPen(Qt.black)
        self.addItem(x_axis)

        step_x = 10000
        for x in range(-self.x_max, self.x_max + 1, step_x):
            text_item = QGraphicsTextItem(str(x))
            text_item.setPos(x / self.kx_compression, -5)
            self.addItem(text_item)

        y_axis = QGraphicsLineItem(0, -self.y_max / self.ky_compression, 0, self.y_max / self.ky_compression)
        y_axis.setPen(Qt.black)
        self.addItem(y_axis)

        step_y = 10000
        for y in range(-self.y_max, self.y_max, step_y):
            if abs(y) < step_y/4:
                continue
            text_item = QGraphicsTextItem(str(y))
            text_item.setPos(1, y / self.ky_compression)
            self.addItem(text_item)

    def add_grid(self):
        grid_group = QGraphicsItemGroup()

        step_x = 10000
        for x in range(-self.x_max, self.x_max + 1, step_x):
            line = QGraphicsLineItem(x / self.kx_compression, -self.y_max / self.ky_compression,
                                     x / self.kx_compression, self.y_max / self.ky_compression)
            line.setPen(Qt.lightGray)
            grid_group.addToGroup(line)

        step_y = 10000
        for y in range(-self.y_max, self.y_max, step_y):
            line = QGraphicsLineItem(-self.x_max / self.kx_compression, y / self.ky_compression,
                                     self.x_max / self.kx_compression, y / self.ky_compression)
            line.setPen(Qt.lightGray)
            grid_group.addToGroup(line)

        self.addItem(grid_group)


class TrajectoryViews(QWidget):
    def __init__(self, pixmaps):
        super().__init__()
        self.clicked_vo = False
        self.clicked_radars = []
        self.clicked_controls = []

        self.pixmaps = pixmaps

        widget_geometry = self.geometry()
        center_x = widget_geometry.x() + widget_geometry.width() / 2
        center_y = widget_geometry.y() + widget_geometry.height() / 2
        self.coordinates_center = np.array([center_x, center_y])

        self.conf_items_models = None

        self.initUI()
        self.chosen_time = 0

    def initUI(self):
        self.view_layout = QVBoxLayout()
        self.scene = TrajGraphicsScene()
        self.view = TrajGraphicsView(self.scene)
        self.setLayout(self.view_layout)
        self.view_layout.addWidget(self.view)

        # self.setGeometry(300, 300, 280, 170)
        self.setWindowTitle('Отображение траекторий')
        self.frameColor = QColor(169, 169, 169)
        # self.show()

    def clearAll(self):
        self.clicked_vo = False
        self.clicked_radars = []
        self.clicked_controls = []

    def menuVOClicked(self, value):
        self.clicked_vo = value
        self.updateAllLines()

    def menuRadarClicked(self, radar_id : int, value : bool):
        if not value:
            if radar_id in self.clicked_radars:
                self.clicked_radars.remove(radar_id)
        else:
            self.clicked_radars.append(radar_id)

        # print(f"List updated: {self.clicked_radars}")
        self.updateAllLines()

    def menuControlClicked(self, control_id : int, value : bool):
        if not value:
            if control_id in self.clicked_controls:
                self.clicked_controls.remove(control_id)
        else:
            self.clicked_controls.append(control_id)

        # print(f"List updated: {self.clicked_controls}")
        self.updateAllLines()

    def updateChosenTime(self, value):
        self.chosen_time = value
        self.updateAllLines()

    def updateAllLines(self):
        self.scene.updateLinesData(self.clicked_radars, self.clicked_controls, self.clicked_vo, self.chosen_time)

    def setTrajectories(self, trajs):
        self.trajectories = trajs
        self.chosen_time = trajs["max_time"]
        self.scene.setLinesData(trajs)
        self.scene.collected_items = []
        self.updateAllLines()

    def setConfItems(self, conf_items):
        self.conf_items_models = conf_items
        for el in self.conf_items_models:
            self.addModelGraphicItem(el)
        self.scene.renderCollectedItems()

    def addModelGraphicItem(self, item):
        pixmap = self.pixmaps[item.model_type // 1000]
        self.scene.addCollectedItem([item, pixmap])


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = QMainWindow()

    window.setWindowTitle('Clickable Graphics View')
    window.show()
    sys.exit(app.exec_())
