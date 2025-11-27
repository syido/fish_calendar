import sys
from typing import TypeVar

from PySide6.QtCore import Qt, QRect, QSize, QEvent
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QApplication, QLabel, QVBoxLayout, \
    QSpacerItem, QDialog, QWidget

from src.app_config import AppInfo, AppUIStyle
from src.utils import WithFont, MyQFont


WidgetT = TypeVar('QWidget', bound="QWidget")
def center(widget: WidgetT) -> WidgetT:
    widget.setAlignment(Qt.AlignCenter)
    return widget

class ItemBox(QDialog):
    def __init__(self, rect: QRect = None):
        super().__init__()
        self.setWindowTitle(" ")
        if not rect is None:
            self.setGeometry(rect)
        self.setFixedSize(QSize(250, 400))
        self.setFont(AppUIStyle.Font.default)
        self.setWindowFlags(Qt.Dialog | Qt.CustomizeWindowHint | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
        
        self.init_ui()
        
    def init_ui(self):
        self.column = QVBoxLayout()
        self.setLayout(self.column)
        
        self.title = WithFont(QLabel("新增日程"), AppUIStyle.Font.big)
        self.column.addWidget(self.title)
        self.column.addStretch()
        