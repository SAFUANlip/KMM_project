import sys
import traceback

import numpy as np
import math

from PyQt5.QtGui import QPainter, QPen, QBrush, QTransform
from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtGui import QPainter, QColor, QFont, QPainterPath
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QPushButton, QHBoxLayout, QWidget
from PyQt5.QtWidgets import (QCheckBox, QHBoxLayout, QWidget, QVBoxLayout, QGraphicsItemGroup,
                             QGraphicsSimpleTextItem, QGraphicsRectItem,  QGraphicsEllipseItem,
                             QGraphicsPathItem, QGraphicsPixmapItem, QSizePolicy)

import sys
from PyQt5.QtWidgets import QApplication, QGraphicsView, QGraphicsScene, QGraphicsItem, QMainWindow
from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsTextItem, QGraphicsLineItem
from PyQt5.QtWidgets import QApplication,  QGraphicsEllipseItem
from PyQt5.QtCore import Qt, QPointF, QRectF
from PyQt5.QtCore import pyqtSignal, QObject


from SimulationAppUI.ConfigureView.Models import RadarSource
from SimulationAppUI.ConfigureView.Grid2D import GraphicsPlotNocksTube, Graphics2DPlotGrid, GraphicsPlotItem

def filter_sorted_traj(traj, time):
    res = []
    for el in traj:
        if el[3] > time:
            break
        res.append(el)
    final_res = [res[0]]
    for i in range(1, len(res)):
        if res[i][0] != res[i - 1][0] or res[i][1] != res[i - 1][1]: #or res[i][2] != res[i - 1][2]:
            final_res.append(res[i])
    return final_res


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



class TargetTrajectorySection(QGraphicsLineItem):
    def __init__(self, point_start, point_end, info, color=Qt.blue):
        super().__init__(point_start[0], point_start[1], point_end[0], point_end[1])
        self.point_start = point_start
        self.point_end = point_end
        self.traj_info = info
        self.setFlags(QGraphicsItem.ItemIsSelectable)
        pen = QPen(color)
        pen.setWidth(1)
        self.setPen(pen)


    def boundingRect(self):
        padding = 2
        return QRectF(self.point_start[0] - padding, self.point_start[1] - padding,
                      self.point_end[0] - self.point_start[0] + padding, self.point_end[1] - self.point_start[1] + padding)

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
        pen = QPen(Qt.red)
        pen.setWidth(1)
        self.setPen(pen)

class TrajGraphicsView(QGraphicsView):
    def __init__(self, scene):
        super().__init__(scene)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setMouseTracking(True)

    def resizeEvent(self, event):
        self.fitInView(self.sceneRect(), Qt.KeepAspectRatio)

class TrajGraphicsScene(QGraphicsScene):
    def __init__(self, lines_data=None, parent=None,):
        super().__init__(parent)
        # self.setSceneRect(-100, -100, 200, 200)  # Устанавливаем размер сцены
        self.trajectories = None
        self.setLinesData(lines_data)
        self.kx_compression = 215
        self.ky_compression = -215
        self.y_max = 100000
        self.x_max = 100000
        self.traj_info_widget = QGraphicsTextItem(f"")
        self.traj_info_widget_rect = QGraphicsTextItem(f"")
        self.chosen_time = 0
        self.collected_items = []
        self.setGrid()

        # for zoom_view
        self.mouse_tracker = MouseTracker()
        # self.setSceneRect(self.itemsBoundingRect())

    def mouseMoveEvent(self, event):
        # print(f"moved: {event.scenePos().x(), event.scenePos().y()}")
        self.mouse_tracker.track_mouse(event)

    def setLinesData(self, data):
        # if not isinstance(data, dict):
        #     return
        self.trajectories = data

    def setGrid(self):
        self.grid = GraphicsPlotItem()
        self.addItem(self.grid)
        self.addItem(self.grid)
        self.grid.setRect(QRectF(0, 0, 1000, 1000))
        self.grid.setAxisText(0, "x, м")
        self.grid.setAxisText(1, "y, м")
        self.grid.setAbscissaRange(-self.x_max, self.x_max)
        self.grid.setOrdinateRange(-self.y_max, self.y_max)
        self.setSceneRect(self.grid.boundingRect())

    def updateLinesData(self, clicked_radars, clicked_controls, clicked_vo, chosen_time=None):
        if not isinstance(self.trajectories, dict):
            return

        self.chosen_time = chosen_time

        # print("updating lines data")
        # print(clicked_controls)
        # print(clicked_vo)
        # print(self.trajectories)
        self.clear()
        self.setGrid()
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
                    self.addTargetTraj(obj_traj, Qt.red)

            if clicked_vo:
                #for key in ["targets", "missiles"]:
                obj_trajs = self.trajectories["vo"]["targets"]
                for key, value in obj_trajs.items():
                    obj_id = key
                    obj_traj = value
                    obj_traj = filter_sorted_traj(obj_traj, self.chosen_time)
                    self.addTargetTraj(obj_traj)
                obj_trajs = self.trajectories["vo"]["missiles"]
                for key, value in obj_trajs.items():
                    obj_id = key
                    obj_traj = value
                    obj_traj = filter_sorted_traj(obj_traj, self.chosen_time)
                    self.addTargetTraj(obj_traj, Qt.red)
        except:
            traceback.print_exc()

        self.update()

    def addTargetTraj(self, obj_traj, color=Qt.blue):
        traj = obj_traj
        for i in range(1, len(traj)):
            point = [traj[i][0] / self.kx_compression, traj[i][1] / self.ky_compression]
            prev_point = [traj[i - 1][0] / self.kx_compression, traj[i - 1][1] / self.ky_compression]
            line = TargetTrajectorySection(point, prev_point, f"section {i}", color)
            center_x = (point[0] + prev_point[0]) / 2
            center_y = (point[1] + prev_point[1]) / 2
            self.addItem(line)
            line.setPos(self.grid.gridItem.mapToScene(center_x, center_y))

    def addTargetPoints(self, obj_traj, color=Qt.blue):
        traj = obj_traj
        for i in range(len(traj)):
            point_coord = [traj[i][0] / self.kx_compression, traj[i][1] / self.ky_compression]
            point = TargetPoint(point_coord, 2, color)
            self.addItem(point)
            point.setPos(self.grid.gridItem.mapToScene(point_coord[0], point_coord[1]))

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
                    self.renderRoundRadarView(center_x, center_y, view_dist_x, view_dist_y)
                elif item.getOverviewMode() == 1:
                    self.renderSectorRadarView(item.pan_angle, item.pan_start, center_x, center_y, view_dist_x, view_dist_y)

            pixmap = item_pair[1]
            pixmap_item = QGraphicsPixmapItem(pixmap)
            # center_x, center_y = x - pixmap.width() / 2, y - pixmap.width() / 2
            center_x, center_y = x, y
            # pixmap_item.setPos(center_x, center_y)
            self.addItem(pixmap_item)
            pixmap_item.setOffset(-pixmap.width() / 2, -pixmap.width() / 2)
            pixmap_item.setPos(self.grid.gridItem.mapToScene(center_x * self.kx_compression, center_y * self.ky_compression))

    def renderRoundRadarView(self, center_x, center_y, view_dist_x, view_dist_y):
        ellipse_item = QGraphicsEllipseItem()
        ellipse_item.setRect(center_x, center_y, 2 * view_dist_x, 2 * view_dist_y)
        brush = QBrush(QColor(0, 255, 0, 18))
        ellipse_item.setBrush(brush)
        self.addItem(ellipse_item)
        ellipse_item.setPos(self.grid.gridItem.mapToScene(center_x, center_y))

    def renderSectorRadarView(self, pan_angle, pan_start, center_x, center_y, view_dist_x, view_dist_y):
        angle = pan_angle
        start_angle = -pan_start - angle
        path = QPainterPath()
        path.moveTo(center_x + view_dist_x, center_y + view_dist_y)
        path.arcTo(center_x, center_y, 2 * view_dist_x, 2 * view_dist_y, start_angle, angle)
        path.lineTo(center_x + view_dist_x, center_y + view_dist_y)
        sector_item = QGraphicsPathItem(path)
        brush = QBrush(QColor(0, 255, 0, 18))
        sector_item.setBrush(brush)
        self.addItem(sector_item)
        sector_item.setPos(self.grid.gridItem.mapToScene(center_x, center_y))


class TrajectoryViews(QWidget):
    def __init__(self, pixmaps):
        super().__init__()
        self.clicked_vo = False
        self.clicked_radars = []
        self.clicked_controls = []

        self.pixmaps = pixmaps

        # widget_geometry = self.geometry()
        # center_x = widget_geometry.x() + widget_geometry.width() / 2
        # center_y = widget_geometry.y() + widget_geometry.height() / 2
        # self.coordinates_center = np.array([center_x, center_y])
        self.coordinates_center = np.array([0, 0])

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



class ZoomGraphicsView(QGraphicsView):
    def __init__(self, main_scene):
        super().__init__(main_scene)
        # self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        # self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        # self.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        # self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        # self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setAlignment(Qt.AlignCenter)

        zoom_rect = QRectF(0, 0, 100, 100)
        self.setSceneRect(zoom_rect)

        self.scale_factor = 10
        self.scale(self.scale_factor, self.scale_factor)

        main_scene.mouse_tracker.mouseMoved.connect(self.update_view)

    def update_view(self, x, y):
        # widget_geometry = self.geometry()
        # center_x = widget_geometry.x() + widget_geometry.width() / 2
        # center_y = widget_geometry.y() + widget_geometry.height() / 2
        # zoom_rect = QRectF(x - 50, y - 50, 100, 100)
        zoom_x = x * self.scale_factor
        zoom_y = y * self.scale_factor
        zoom_width = 50
        zoom_height = 50

        zoom_rect = QRectF(x - zoom_width / 2, y - zoom_height / 2, zoom_width, zoom_height)

        self.setSceneRect(zoom_rect)
        self.update()
        self.repaint()

class MouseTracker(QObject):
    mouseMoved = pyqtSignal(int, int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent

    def track_mouse(self, event):
        pos = event.scenePos()
        self.mouseMoved.emit(pos.x(), pos.y())
        # print(f"emmited: {pos.x(), pos.y()}")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = QMainWindow()

    window.setWindowTitle('Clickable Graphics View')
    window.show()
    sys.exit(app.exec_())
