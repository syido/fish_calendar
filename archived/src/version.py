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

class VersionBox(QDialog):
    def __init__(self, rect: QRect = None):
        super().__init__()
        self.setWindowTitle(f"关于{AppInfo.app_name}")
        if not rect is None:
            self.setGeometry(rect)
        self.setFixedSize(QSize(350, 250))
        self.setFont(AppUIStyle.Font.default)
        self.setWindowFlags(Qt.Dialog | Qt.CustomizeWindowHint | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
        
        column = QVBoxLayout()
        column.setAlignment(Qt.AlignHCenter)
        column.setSpacing(0)
        self.setLayout(column)
        
        column.addSpacerItem(QSpacerItem(0, 10))
        
        app_icon = center(QLabel())
        app_icon.setPixmap(QPixmap(AppInfo.app_icon))
        app_icon.setScaledContents(True)
        app_icon.setFixedSize(64, 64)
        column.addWidget(app_icon, alignment=Qt.AlignHCenter)
        
        column.addSpacerItem(QSpacerItem(0, 30))

        name_label = center(WithFont(QLabel(AppInfo.app_name), MyQFont(12, True)))
        column.addWidget(name_label)
        
        column.addSpacerItem(QSpacerItem(0, 20))
        column.addWidget(center(QLabel("由 syido 用 ❤️ 制作")))
        
        column.addStretch()
        version_info = center(WithFont(QLabel(f'1.0.0 · 2025.9.19'), AppUIStyle.Font.small))
        version_info.setStyleSheet("color: #8d8d8d;")
        column.addWidget(version_info)
        
        link_info = center(WithFont(QLabel(f'{AppInfo.link} | {AppInfo.license}'), AppUIStyle.Font.small))
        link_info.setStyleSheet("color: #8d8d8d;")
        link_info.setOpenExternalLinks(True)
        column.addWidget(link_info)
        
    def event(self, e):
        if e.type() == QEvent.WindowDeactivate:  # 窗口失活
            self.close()
        return super().event(e)