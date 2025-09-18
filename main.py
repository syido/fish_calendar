import sys

from PySide6.QtWidgets import QApplication

from src.fish_calender import FishCalenderApp


def main():
    app = QApplication(sys.argv)
    window = FishCalenderApp()
    
    if not "-s" in sys.argv: 
        window.show()
        
    sys.exit(app.exec())

if __name__ == '__main__':
    main()