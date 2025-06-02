"""Main entry point for the RC circuit simulator application."""

import sys
from PyQt6.QtWidgets import QApplication    # pylint: disable=no-name-in-module
from rc_simulator import RCSimulator        # pylint: disable=import-error


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RCSimulator()
    window.show()
    sys.exit(app.exec())
