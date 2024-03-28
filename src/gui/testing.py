from PyQt5.QtWidgets import QApplication
import sys
import pathlib

from PyQt5.QtCore import Qt, QLineF, QMimeData
from PyQt5.QtWidgets import QMainWindow, QAction, QMenu, QGraphicsScene, QGraphicsView, QGraphicsPixmapItem, QGraphicsItem
from PyQt5.QtGui import QPixmap, QBrush
from ConfiguratingViewport import ConfiguratingViewport

class MainWindow(QMainWindow):
    """
    Main window to chose between checker and redactor
    """
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle('MainWindow')
        self.setMinimumWidth(1248)
        self.setMinimumHeight(768)


class TestGraphicItem(QGraphicsPixmapItem):
    def __init__(self, pixmap, parent = None):
        super(TestGraphicItem, self).__init__(pixmap, parent)
        self.__create_actions()
        self.setAcceptedMouseButtons(Qt.LeftButton)
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)

    def __create_actions(self):
        self.del_action = QAction('Удалить')
        self.del_action.triggered.connect(self.delete)

    def delete(self):
        print("delete")

    def contextMenuEvent(self, event):
        context_menu = QMenu()
        context_menu.setStyleSheet('background-color: gray;')
        context_menu.addAction(self.del_action)
        selectedAction = context_menu.exec(event.screenPos())

    def mouseMoveEvent(self, event):
        if QLineF(event.screenPos(), event.buttonDownScreenPos(Qt.LeftButton)).length() < QApplication.startDragDistance(): 
            return
        super().mouseMoveEvent(event)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    #w = MainWindow()
    #w.show()
    #scene = QGraphicsScene(0, 0, 1248, 768)
    pixmaps = {1 : QPixmap(str(pathlib.Path().resolve() / 'src/gui/resources/test.jpg')).scaledToHeight(100), 
               2 : QPixmap(str(pathlib.Path().resolve() / 'src/gui/resources/test2.jpg')).scaledToHeight(100),
               3 : QPixmap(str(pathlib.Path().resolve() / 'src/gui/resources/test3.jpg')).scaledToHeight(100),
               4 : QPixmap(str(pathlib.Path().resolve() / 'src/gui/resources/test4.jpg')).scaledToHeight(100)}
    #item = TestGraphicItem(image)
    #item = SimpleGraphicComponent(image, QApplication.startDragDistance())
    #item.setPos(100, 100)
    #item.posChanged.connect(lambda : print("gsgsgsg"))
    #scene.addItem(item)
    #item.setRotation(45)
    #item2 = QGraphicsEllipseItem(100, 200, 100, 300)
    #item2.setBrush(QBrush(Qt.red, style = Qt.SolidPattern))
    #item2.setPos(420, 220)
    #scene.addItem(item2)

    #view = QGraphicsView(scene)
    #view.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
    #view.show()
    viewport = ConfiguratingViewport(pixmaps, QApplication.startDragDistance())
    viewport.addItem(1000, 100, 100)
    viewport.addItem(2000, 200, 300)
    viewport.addItem(2000, 500, 600)
    viewport.addItem(3000, 200, 500)
    viewport.addItem(4000, 650, 150)
    sys.exit(app.exec_())