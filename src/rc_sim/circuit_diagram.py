from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QPen, QBrush, QColor
from PyQt6.QtCore import QRectF
import numpy as np


class CircuitDiagram(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(200, 100)
        self.charge_level = 0.0


    def set_charge_level(self, Vc, V0):
        self.charge_level = Vc / V0 if V0 != 0 else 0.0
        self.update()


    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        pen = QPen(QColor("#ffffff"), 2)
        painter.setPen(pen)

        # Рисуем источник питания
        painter.drawLine(10, 50, 30, 50)
        painter.drawLine(20, 40, 20, 60)  # Батарея

        # Рисуем резистор
        painter.drawLine(30, 50, 70, 50)
        painter.drawRect(QRectF(70, 40, 40, 20))

        # Рисуем конденсатор
        painter.drawLine(110, 50, 130, 50)
        painter.drawLine(130, 30, 130, 70)
        painter.drawLine(150, 30, 150, 70)
        painter.drawLine(150, 50, 190, 50)

        # Визуализация заряда
        painter.setBrush(QBrush(QColor(255, 255, 0, int(255 * self.charge_level))))
        painter.drawRect(QRectF(140, 30, 10, 40))
