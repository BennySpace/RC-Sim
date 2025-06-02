"""Module for displaying an RC circuit diagram with charge visualization."""

from typing import Optional
from PyQt6.QtWidgets import QWidget                     # pylint: disable=no-name-in-module
from PyQt6.QtGui import QPainter, QPen, QBrush, QColor  # pylint: disable=no-name-in-module
from PyQt6.QtCore import QRectF                         # pylint: disable=no-name-in-module


class CircuitDiagram(QWidget):
    """Widget to display an RC circuit diagram with charge visualization."""
    # Constants for diagram dimensions
    DIAGRAM_WIDTH: int = 200
    DIAGRAM_HEIGHT: int = 120
    LINE_THICKNESS: int = 2
    BATTERY_X: int = 10
    BATTERY_Y: int = 50
    BATTERY_WIDTH: int = 20
    R_INT_X: int = 50
    R_INT_WIDTH: int = 30
    RESISTOR_X: int = 100
    RESISTOR_WIDTH: int = 40
    CAPACITOR_X: int = 160
    CAPACITOR_WIDTH: int = 20
    CHARGE_RECT_X: int = 170
    CHARGE_RECT_WIDTH: int = 10
    CHARGE_RECT_HEIGHT: int = 40
    LABEL_OFFSET_Y: int = 20

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """Initialize the circuit diagram widget."""
        super().__init__(parent)
        self.setFixedSize(self.DIAGRAM_WIDTH, self.DIAGRAM_HEIGHT)
        self.charge_level: float = 0.0

    def set_charge_level(self, vc: float, v0: float) -> None:
        """Set the charge level for visualization.

        Args:
            vc: Current voltage across the capacitor.
            v0: Source EMF (electromotive force).
        """
        self.charge_level = vc / v0 if v0 != 0 else 0.0
        self.update()

    def paintEvent(self, event: QPainter) -> None:  # pylint: disable=invalid-name,unused-argument
        """Paint the RC circuit diagram.

        Args:
            event: The paint event triggering the redraw.
        """
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        pen = QPen(QColor("#ffffff"), self.LINE_THICKNESS)
        painter.setPen(pen)

        # Draw power source (battery)
        painter.drawLine(self.BATTERY_X, self.BATTERY_Y,
                         self.BATTERY_X + self.BATTERY_WIDTH, self.BATTERY_Y)
        painter.drawLine(self.BATTERY_X + self.BATTERY_WIDTH // 2,
                         self.BATTERY_Y - 10,
                         self.BATTERY_X + self.BATTERY_WIDTH // 2,
                         self.BATTERY_Y + 10)
        painter.drawText(self.BATTERY_X, self.BATTERY_Y - self.LABEL_OFFSET_Y, "E")

        # Draw internal resistance (R_int)
        painter.drawLine(self.BATTERY_X + self.BATTERY_WIDTH, self.BATTERY_Y,
                         self.R_INT_X, self.BATTERY_Y)
        painter.drawRect(QRectF(self.R_INT_X, self.BATTERY_Y - 10,
                               self.R_INT_WIDTH, 20))
        painter.drawText(self.R_INT_X + 5, self.BATTERY_Y + self.LABEL_OFFSET_Y, "R_int")

        # Draw resistor (R)
        painter.drawLine(self.R_INT_X + self.R_INT_WIDTH, self.BATTERY_Y,
                         self.RESISTOR_X, self.BATTERY_Y)
        painter.drawRect(QRectF(self.RESISTOR_X, self.BATTERY_Y - 10,
                               self.RESISTOR_WIDTH, 20))
        painter.drawText(self.RESISTOR_X + 10, self.BATTERY_Y + self.LABEL_OFFSET_Y, "R")

        # Draw capacitor (C)
        painter.drawLine(self.RESISTOR_X + self.RESISTOR_WIDTH, self.BATTERY_Y,
                         self.CAPACITOR_X, self.BATTERY_Y)
        painter.drawLine(self.CAPACITOR_X, self.BATTERY_Y - 20,
                         self.CAPACITOR_X, self.BATTERY_Y + 20)
        painter.drawLine(self.CAPACITOR_X + self.CAPACITOR_WIDTH,
                         self.BATTERY_Y - 20,
                         self.CAPACITOR_X + self.CAPACITOR_WIDTH,
                         self.BATTERY_Y + 20)
        painter.drawLine(self.CAPACITOR_X + self.CAPACITOR_WIDTH, self.BATTERY_Y,
                         self.DIAGRAM_WIDTH - 10, self.BATTERY_Y)
        painter.drawText(self.CAPACITOR_X + self.CAPACITOR_WIDTH // 2,
                         self.BATTERY_Y + self.LABEL_OFFSET_Y + 20, "C")

        # Visualize charge level
        painter.setBrush(QBrush(QColor(255, 255, 0, int(255 * self.charge_level))))
        painter.drawRect(QRectF(self.CHARGE_RECT_X, self.BATTERY_Y - self.CHARGE_RECT_HEIGHT // 2,
                               self.CHARGE_RECT_WIDTH, self.CHARGE_RECT_HEIGHT))
        painter.end()
