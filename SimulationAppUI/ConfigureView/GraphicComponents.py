from PyQt5.QtWidgets import QGraphicsPixmapItem, QGraphicsObject, QGraphicsEllipseItem, QAction, QMenu
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


class RadarGraphicComponent(SimpleGraphicComponent):
    def __init__(self, pixmap, start_drag_distance, grid, parent = None):
        super(RadarGraphicComponent, self).__init__(pixmap, start_drag_distance, grid, parent)
        self.round = QGraphicsEllipseItem()
        self.round.setBrush(QColor(0,0,255,10))
        self.sector = QGraphicsEllipseItem()
        self.sector.setPen(Qt.red)
        self.sector.setStartAngle(0)
        self.sector.setSpanAngle(0)

    def setSector(self, start_angle, span):
        self.sector.setStartAngle(16 * start_angle)
        self.sector.setSpanAngle(16 * span)
