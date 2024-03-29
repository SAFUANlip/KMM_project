from PyQt5.QtWidgets import QGraphicsPixmapItem, QGraphicsObject, QAction, QMenu
from PyQt5.QtCore import  Qt, QLineF, QPointF, QRectF, QObject, pyqtSignal
from PyQt5.QtGui import QColor

class SimpleGraphicComponent(QGraphicsObject):

    posChanged = pyqtSignal()

    def __init__(self, pixmap, start_drag_distance, parent = None):
        super(SimpleGraphicComponent, self).__init__(parent)
        self.pixmap = pixmap
        self.start_drag_distance = start_drag_distance
        self.__create_actions()
        self.setAcceptedMouseButtons(Qt.LeftButton)
        self.setFlags(self.flags() | QGraphicsPixmapItem.ItemIsMovable |
                      QGraphicsPixmapItem.ItemIsSelectable | 
                      QGraphicsPixmapItem.ItemSendsGeometryChanges)

    def __create_actions(self):
        self.configurate_action = QAction('Изменить')
        self.del_action = QAction('Удалить')
        
    def contextMenuEvent(self, event):
        context_menu = QMenu()
        context_menu.setStyleSheet('background-color: gray;')
        context_menu.addAction(self.configurate_action)
        context_menu.addAction(self.del_action)
        selectedAction = context_menu.exec(event.screenPos())

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
    def __init__(self, pixmap, start_drag_distance, parent = None):
        super(RadarGraphicComponent, self).__init__(pixmap, start_drag_distance, parent)
        self.radiusx = 0
        self.radiusy = 0
        self.arc_len = 0
        self.direction = 0
        self.is_round = True

    def paint(self, painter, option, widget):
        if self.is_round:
            painter.setBrush(QColor(0,0,255,10))
            painter.drawEllipse(QPointF(0, 0), self.radiusx, self.radiusy)
            painter.setBrush(Qt.NoBrush)
        painter.setPen(Qt.red)
        painter.drawPie(-self.radiusx, -self.radiusy, 2*self.radiusx, 2*self.radiusy,
                        self.direction*16, self.arc_len*16)
        painter.setPen(Qt.black)
        super().paint(painter, option, widget)
