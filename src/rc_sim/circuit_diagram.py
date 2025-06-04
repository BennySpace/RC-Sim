"""
Module for displaying an RC circuit diagram with animated charge and current visualization.

This module provides the `CircuitDiagram` class, a PyQt6 widget that renders a graphical
representation of an RC circuit, including a battery, resistors, capacitor, and animated
current flow and charge level indicators.
"""

# pylint: disable=no-name-in-module
from typing import Optional
from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QPen, QBrush, QColor, QFont, QPolygonF
from PyQt6.QtCore import QRectF, QTimer, QPointF
# pylint: enable=no-name-in-module


class CircuitDiagram(QWidget):
    """Widget to display an RC circuit diagram with charge and current animation."""

    DIAGRAM_WIDTH: int = 250
    DIAGRAM_HEIGHT: int = 150
    LINE_THICKNESS: int = 2
    FONT_SIZE: int = 10

    BATTERY_X: int = 10
    BATTERY_Y: int = 75
    BATTERY_WIDTH: int = 25

    R_INT_X: int = 55
    R_INT_WIDTH: int = 45

    RESISTOR_X: int = 110
    RESISTOR_WIDTH: int = 55

    CAPACITOR_X: int = 180
    CAPACITOR_WIDTH: int = 35

    CHARGE_RECT_X: int = 190
    CHARGE_RECT_WIDTH: int = 25
    CHARGE_RECT_HEIGHT: int = 50

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """Initialize the circuit diagram widget."""
        super().__init__(parent)
        self.setFixedSize(self.DIAGRAM_WIDTH, self.DIAGRAM_HEIGHT)
        self.charge_level: float = 0.0

        self.current_arrow_pos = self.BATTERY_X + self.BATTERY_WIDTH + 5
        self.arrow_timer = QTimer(self)
        self.arrow_timer.timeout.connect(self.update_arrow_position)
        self.arrow_timer.start(100)  # Update every 100 ms

    def set_charge_level(self, vc: float, v0: float) -> None:
        """Set the charge level for visualization."""
        self.charge_level = vc / v0 if v0 != 0 else 0.0
        self.update()

    def update_arrow_position(self) -> None:
        """Update position of current arrow and repaint."""
        end_pos = self.CAPACITOR_X + self.CAPACITOR_WIDTH
        if self.current_arrow_pos < end_pos:
            self.current_arrow_pos += 5
        else:
            self.current_arrow_pos = self.BATTERY_X + self.BATTERY_WIDTH + 5
        self.update()

    # pylint: disable=invalid-name, unused-argument
    def paintEvent(self, event) -> None:
        """Paint the RC circuit diagram."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        pen = QPen(QColor("#ffffff"), self.LINE_THICKNESS)
        painter.setPen(pen)
        painter.setFont(QFont("Arial", self.FONT_SIZE))

        # --- Draw circuit components ---

        # Battery
        painter.drawLine(self.BATTERY_X, self.BATTERY_Y,
                         self.BATTERY_X + self.BATTERY_WIDTH, self.BATTERY_Y)
        painter.drawLine(self.BATTERY_X + self.BATTERY_WIDTH // 2,
                         self.BATTERY_Y - 12,
                         self.BATTERY_X + self.BATTERY_WIDTH // 2,
                         self.BATTERY_Y + 12)
        painter.drawText(self.BATTERY_X, self.BATTERY_Y - 5, "E")

        # R_int
        r_int_rect = QRectF(self.R_INT_X, self.BATTERY_Y - 15, self.R_INT_WIDTH, 30)
        painter.drawLine(self.BATTERY_X + self.BATTERY_WIDTH, self.BATTERY_Y,
                         self.R_INT_X, self.BATTERY_Y)
        painter.drawRect(r_int_rect)
        painter.drawText(r_int_rect, 0x84, "R_int")

        # R
        resistor_rect = QRectF(self.RESISTOR_X, self.BATTERY_Y - 15,
                               self.RESISTOR_WIDTH, 30)
        painter.drawLine(self.R_INT_X + self.R_INT_WIDTH, self.BATTERY_Y,
                         self.RESISTOR_X, self.BATTERY_Y)
        painter.drawRect(resistor_rect)
        painter.drawText(resistor_rect, 0x84, "R")

        # Capacitor
        painter.drawLine(self.RESISTOR_X + self.RESISTOR_WIDTH, self.BATTERY_Y,
                         self.CAPACITOR_X, self.BATTERY_Y)
        painter.drawLine(self.CAPACITOR_X, self.BATTERY_Y - 25,
                         self.CAPACITOR_X, self.BATTERY_Y + 25)
        painter.drawLine(self.CAPACITOR_X + self.CAPACITOR_WIDTH,
                         self.BATTERY_Y - 25,
                         self.CAPACITOR_X + self.CAPACITOR_WIDTH,
                         self.BATTERY_Y + 25)
        painter.drawLine(self.CAPACITOR_X + self.CAPACITOR_WIDTH,
                         self.BATTERY_Y,
                         self.DIAGRAM_WIDTH - 10, self.BATTERY_Y)
        painter.drawText(self.CAPACITOR_X + 18, self.BATTERY_Y, "C")

        # --- Draw charge level ---
        painter.setBrush(QBrush(QColor(255, 255, 0, int(255 * self.charge_level))))
        painter.drawRect(QRectF(self.CHARGE_RECT_X, self.BATTERY_Y - self.CHARGE_RECT_HEIGHT // 2,
                                self.CHARGE_RECT_WIDTH, self.CHARGE_RECT_HEIGHT))

        # --- Draw animated current arrow ---
        self.draw_current_arrow(painter)

        painter.end()
    # pylint: enable=invalid-name, unused-argument

    def draw_current_arrow(self, painter: QPainter) -> None:
        """Draw a small arrow indicating current movement."""
        arrow_size = 9
        y = self.BATTERY_Y

        path = QPolygonF([
            QPointF(self.current_arrow_pos, y - arrow_size // 2),
            QPointF(self.current_arrow_pos + arrow_size, y),
            QPointF(self.current_arrow_pos, y + arrow_size // 2)
        ])

        painter.setBrush(QBrush(QColor("green")))
        painter.drawPolygon(path)

        painter.setPen(QColor("white"))
        painter.setFont(QFont("Arial", self.FONT_SIZE))
        painter.drawText(self.current_arrow_pos - 5, y - 5, "I(А)")
