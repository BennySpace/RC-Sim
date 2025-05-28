import sys
from PyQt6.QtWidgets import QApplication
from rc_simulator import RCSimulator

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RCSimulator()
    window.show()
    sys.exit(app.exec())