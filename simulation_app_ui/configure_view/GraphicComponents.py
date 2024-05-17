from PyQt5.QtWidgets import QGraphicsPixmapItem, QGraphicsObject, QGraphicsEllipseItem, QGraphicsLineItem, QAction, QMenu
from PyQt5.QtCore import  Qt, QLineF, QPointF, QRectF, QObject, pyqtSignal
from PyQt5.QtGui import QColor

class SimpleGraphicComponent(QGraphicsObject):

    posChanged = pyqtSignal()

    def __init__(self, pixmap, start_drag_distance, grid, parent = None):
        super(SimpleGraphicComponent, self).__init__(parent)
        self.pixmap = pixmap
        self.start_drag_distance = start_drag_distance
        self.grid = grid
        self.__create_actions()
        self.setAcceptedMouseButtons(Qt.LeftButton)
        self.setFlags(self.flags() | QGraphicsPixmapItem.ItemIsMovable |
                      QGraphicsPixmapItem.ItemIsSelectable | 
                      QGraphicsPixmapItem.ItemSendsGeometryChanges | 
                      QGraphicsPixmapItem.ItemSendsScenePositionChanges)

    def __create_actions(self):
        self.configurate_action = QAction('Изменить')
        self.del_action = QAction('Удалить')
        
    def contextMenuEvent(self, event):
        context_menu = QMenu()
        context_menu.setStyleSheet('background-color: gray;')
        context_menu.addAction(self.configurate_action)
        context_menu.addAction(self.del_action)
        selectedAction = context_menu.exec(event.screenPos())

    def itemChange(self, change, value):
        if change == QGraphicsPixmapItem.ItemPositionChange and self.grid:
            newPos = self.grid.mapFromScene(value)
            if not self.grid.boundingRect().contains(newPos):
                newPos.setX(min(self.grid.boundingRect().right(), max(newPos.x(), self.grid.boundingRect().left())))
                newPos.setY(min(self.grid.boundingRect().bottom(), max(newPos.y(), self.grid.boundingRect().top())))
                return self.grid.mapToScene(newPos)
        return super().itemChange(change, value)

    def mouseMoveEvent(self, event):
        if QLineF(event.screenPos(), event.buttonDownScreenPos(Qt.LeftButton)).length() < self.start_drag_distance: 
            return
        self.posChanged.emit()
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self.posChanged.emit()
        super().mouseReleaseEvent(event)

    def boundingRect(self):
        return QRectF(-self.pixmap.width()//2, -self.pixmap.height()//2, self.pixmap.width(), self.pixmap.height())

    def paint(self, painter, option, widget):
        painter.drawPixmap(QPointF(-self.pixmap.width()//2, -self.pixmap.height()//2), self.pixmap)


class GraphicAeroTargetComponent(SimpleGraphicComponent):
    def __init__(self, pixmap, start_drag_distance, grid, parent = None):
        super(GraphicAeroTargetComponent, self).__init__(pixmap, start_drag_distance, grid, parent)
        self.__create_actions()

    def __create_actions(self):
        self.add_track_action = QAction('Задать траекторию')
        self.del_track_action = QAction('Удалить траекторию')
        self.del_track_action.setVisible(False)
        self.configurate_action = QAction('Изменить')
        self.del_action = QAction('Удалить')
        
    def contextMenuEvent(self, event):
        context_menu = QMenu()
        context_menu.setStyleSheet('background-color: gray;')
        context_menu.addAction(self.add_track_action)
        context_menu.addAction(self.del_track_action)
        context_menu.addAction(self.configurate_action)
        context_menu.addAction(self.del_action)
        selectedAction = context_menu.exec(event.screenPos())


class RadarGraphicComponent(SimpleGraphicComponent):
    def __init__(self, pixmap, start_drag_distance, grid, parent = None):
        super(RadarGraphicComponent, self).__init__(pixmap, start_drag_distance, grid, parent)
        self.round = QGraphicsEllipseItem()
        self.round.setBrush(QColor(0,0,255,10))

        self.sector = QGraphicsEllipseItem()
        self.sector.setPen(Qt.red)
        self.sector.setStartAngle(0)
        self.sector.setSpanAngle(0)

        self.whole_sector = QGraphicsEllipseItem()
        self.whole_sector.setBrush(QColor(0,0,255,10))
        self.whole_sector.setStartAngle(0)
        self.whole_sector.setSpanAngle(0)

    def setSector(self, start_angle, span):
        self.sector.setStartAngle(16 * start_angle)
        self.sector.setSpanAngle(16 * span)

    def setWholeSector(self, start_angle, span):
        self.whole_sector.setStartAngle(16 * start_angle)
        self.whole_sector.setSpanAngle(16 * span)


class PointGraphicComponent(SimpleGraphicComponent):

    addPointRequest = pyqtSignal()
    configurateRequested = pyqtSignal(QObject)
    deleteRequest = pyqtSignal(QObject)

    def __init__(self, start_drag_distance, grid, parent = None):
        super(PointGraphicComponent, self).__init__(None, start_drag_distance, grid, parent)
        self.is_collided = False
        self.left_line = None
        self.right_line = None
        self.__create_actions()


    def __create_actions(self):
        self.add_point_action = QAction('Добавить точку')
        self.add_point_action.triggered.connect(lambda: self.addPointRequest.emit())
        self.configurate_action = QAction('Изменить')
        self.configurate_action.triggered.connect(lambda: self.configurateRequested.emit(self))
        self.del_action = QAction('Удалить')
        self.del_action.triggered.connect(lambda: self.deleteRequest.emit(self))

    def contextMenuEvent(self, event):
        context_menu = QMenu()
        context_menu.setStyleSheet('background-color: gray;')
        context_menu.addAction(self.add_point_action)
        context_menu.addAction(self.configurate_action)
        context_menu.addAction(self.del_action)
        selectedAction = context_menu.exec(event.screenPos())

    def boundingRect(self):
        return QRectF(-5, -5, 10, 10)

    def paint(self, painter, option, widget):
        if self.is_collided:
            painter.setBrush(Qt.red)
        else:
            painter.setBrush(Qt.blue)
        painter.drawEllipse(self.boundingRect())


class LineGraphicComponent(QGraphicsLineItem):
    def __init__(self, parent=None):
        super(LineGraphicComponent, self).__init__(parent)
        self.left_point = None
        self.right_point = None

    def paint(self, painter, option, widget):
        if self.left_point and self.right_point:
            self.setLine(self.left_point.x(), self.left_point.y(),
                         self.right_point.x(), self.right_point.y())
            super().paint(painter, option, widget)
