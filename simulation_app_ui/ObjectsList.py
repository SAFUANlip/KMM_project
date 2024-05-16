# import sys
# from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
#                              QHBoxLayout, QToolBar, QListWidget, QTextEdit,
#                              QAction)
#
# from PyQt5.QtWidgets import QPushButton, QListWidgetItem
# from PyQt5.QtGui import QIcon
#
#
# class ObjectsList(QListWidget()):
#     def __init__(self):
#         super().__init__()
#
#     def setElements(self, func):
#         for i in range(20):
#             item = QListWidgetItem()
#             button = QPushButton(text=f"Item{i}", parent=self)
#             button.clicked.connect(func)
#
#             button.setIcon(QIcon("./images/aircraft_icon.png"))
#
#             item.setSizeHint(button.sizeHint())
#             self.addItem(item)
#             self.setItemWidget(item, button)