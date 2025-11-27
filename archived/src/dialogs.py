from PySide6.QtWidgets import QApplication, QMessageBox, QWidget
from typing import Optional

class Dialog:
    Yes = QMessageBox.Yes
    No = QMessageBox.No
    
    @staticmethod
    def confirm(parent: Optional[QWidget], title: str, text: str):
        return QMessageBox.question(parent, title, text, QMessageBox.Yes | QMessageBox.No)
    
    @staticmethod
    def alarm(parent: Optional[QWidget], title: str, text: str):
        return QMessageBox.warning(None, title, text)