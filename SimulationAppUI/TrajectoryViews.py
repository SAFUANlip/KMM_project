import sys
# from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
#                              QHBoxLayout, QToolBar, QListWidget, QTextEdit,
#                              QAction)

from PyQt5.QtGui import QPainter, QPen, QBrush
from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtGui import QPainter, QColor, QFont
from PyQt5.QtCore import Qt


class TrajectoryViews(QWidget):

    def __init__(self):
        super().__init__()
        self.exampleTraj = [(i * 10, i * 10) for i in range(10)]
        self.initUI()


    def initUI(self):
        # self.setGeometry(300, 300, 280, 170)
        self.setWindowTitle('TrajView')
        self.frameColor = QColor(169, 169, 169)
        # self.show()


    def paintEvent(self, event):
        qp = QPainter()
        qp.begin(self)
        self.drawFrame(qp)
        self.drawTraj(event, qp)
        qp.end()

    def drawFrame(self, qp):
        pen = QPen(self.frameColor)
        pen.setWidth(4)
        qp.setPen(pen)
        qp.drawRect(0, 0, self.width() - 1, self.height() - 1)

    def drawTraj(self, event, qp):

        qp.setPen(QColor(168, 34, 3))
        qp.setFont(QFont('Decorative', 12))

        for i in range(1, len(self.exampleTraj)):
            point = self.exampleTraj[i]
            prev_point = self.exampleTraj[i - 1]
            qp.drawLine(point[0], point[1], prev_point[0], prev_point[1])
            qp.drawEllipse(point[0], point[1], 5, 5)

        qp.setPen(QColor(0, 0, 100))
        qp.drawText(self.exampleTraj[-1][0], self.exampleTraj[-1][1], 'TrajExample')



if __name__ == '__main__':

    app = QApplication(sys.argv)
    ex = TrajectoryViews()
    sys.exit(app.exec_())
