"""Module for displaying a help window with RC circuit information and equations."""

import os
import tempfile
import uuid
from typing import Optional
import matplotlib.pyplot as plt
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QScrollArea, QWidget  # pylint: disable=no-name-in-module
from PyQt6.QtGui import QPixmap                                                 # pylint: disable=no-name-in-module
from PyQt6.QtCore import Qt                                                     # pylint: disable=no-name-in-module


class HelpWindow(QDialog):
    """Dialog window to display RC circuit information and equations."""

    # Constants for window and formula rendering
    WINDOW_X: int = 200
    WINDOW_Y: int = 200
    WINDOW_WIDTH: int = 700
    WINDOW_HEIGHT: int = 500
    FIGURE_WIDTH: float = 4.0
    FIGURE_HEIGHT: float = 1.0
    FIGURE_DPI: int = 100
    FIGURE_PAD: float = 0.1
    FONT_SIZE: int = 14
    STYLESHEET: str = (
        "QDialog { background-color: #000000; color: #ffffff; } "
        "QLabel { color: #ffffff; font-size: 16px; font-family: Arial; } "
        "QLabel.header { color: #4da8da; font-size: 20px; font-weight: bold; margin: 10px 0; } "
        "QLabel.formula { margin: 10px 0; }"
    )
    DESCRIPTION_TEXT: str = (
        "Это приложение моделирует поведение RC-цепи (резистор-конденсатор) при "
        "постоянном (DC) или переменном (AC) напряжении с учётом неидеального источника "
        "питания. Основные параметры:\n"
        "- Ёмкость (C): в микрофарадах (мкФ).\n"
        "- Сопротивление (R): в омах (Ом).\n"
        "- Внутреннее сопротивление источника (R_int): в омах (Ом).\n"
        "- ЭДС (E): амплитуда источника (В).\n"
        "- Температурный коэффициент (α): влияет на сопротивление при изменении температуры.\n"
        "- Температура (T): влияет на сопротивление через формулу "
        "R_total = (R + R_int)(1 + α(T - 25))."
    )

    def __init__(self, parent: Optional[QDialog] = None) -> None:
        """Initialize the help window."""
        super().__init__(parent)
        self.setWindowTitle("Справка: RC-цепь")
        self.setGeometry(self.WINDOW_X, self.WINDOW_Y,
                         self.WINDOW_WIDTH, self.WINDOW_HEIGHT)
        self.temp_files: list[str] = []
        self.setup_ui()

    def setup_ui(self) -> None:  # pylint: disable=too-many-locals
        """Set up the UI for the help window."""
        layout = QVBoxLayout(self)
        container = QWidget()
        container_layout = QVBoxLayout(container)

        self.setStyleSheet(self.STYLESHEET)

        title_label = QLabel("Справочная информация по RC-цепи")
        title_label.setProperty("class", "header")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        container_layout.addWidget(title_label)

        description = QLabel(self.DESCRIPTION_TEXT)
        description.setWordWrap(True)
        container_layout.addWidget(description)

        formulas_label = QLabel("Формулы")
        formulas_label.setProperty("class", "header")
        container_layout.addWidget(formulas_label)

        dc_label = QLabel("Для постоянного тока (DC):")
        dc_label.setProperty("class", "header")
        dc_label.setStyleSheet("font-size: 16px; color: #4da8da;")
        container_layout.addWidget(dc_label)

        dc_formulas = [
            (r"V_C(t) = E \left(1 - e^{-t / \tau}\right)", "Напряжение на конденсаторе (зарядка)"),
            (r"V_C(t) = E e^{-t / \tau}", "Напряжение на конденсаторе (разрядка)"),
            (r"I(t) = \frac{E}{R + R_{\text{int}}} e^{-t / \tau}", "Ток (зарядка)"),
            (r"\tau = (R + R_{\text{int}}) \cdot C", "Постоянная времени")
        ]

        for formula, desc in dc_formulas:
            container_layout.addWidget(self.create_formula_label(formula, desc))

        ac_label = QLabel("Для переменного тока (AC):")
        ac_label.setProperty("class", "header")
        ac_label.setStyleSheet("font-size: 16px; color: #4da8da;")
        container_layout.addWidget(ac_label)

        ac_formulas = [
            (r"Z = \sqrt{(R + R_{\text{int}})^2 + \frac{1}{(\omega C)^2}}", "Импеданс"),
            (r"V_C(t) = \frac{E \sin(\omega t)}{\sqrt{1 + (\omega (R + R_{\text{int}}) C)^2}}", "Напряжение"),              # pylint: disable=line-too-long
            (r"I(t) = \frac{E}{Z} \sin\left(\omega t - \arctan\left(\frac{1}{\omega (R + R_{\text{int}}) C}\right)\right)", # pylint: disable=line-too-long
             "Ток")
        ]

        for formula, desc in ac_formulas:
            container_layout.addWidget(self.create_formula_label(formula, desc))

        energy_label = QLabel("Энергетические характеристики:")
        energy_label.setProperty("class", "header")
        energy_label.setStyleSheet("font-size: 16px; color: #4da8da;")
        container_layout.addWidget(energy_label)

        energy_formulas = [
            (r"E = \frac{1}{2} C V_C^2", "Энергия конденсатора"),
            (r"P = \text{mean}(I^2 (R + R_{\text{int}}))", "Тепловые потери")
        ]

        for formula, desc in energy_formulas:
            container_layout.addWidget(self.create_formula_label(formula, desc))

        container_layout.addStretch()
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(container)
        layout.addWidget(scroll_area)

    def create_formula_label(self, formula: str, description: str) -> QLabel:
        """Create a label with a rendered LaTeX formula.

        Args:
            formula: LaTeX string for the formula.
            description: Description of the formula.

        Returns:
            QLabel with the rendered formula image and description.
        """
        temp_file = os.path.join(tempfile.gettempdir(), f"formula_{uuid.uuid4()}.png")
        plt.figure(figsize=(self.FIGURE_WIDTH, self.FIGURE_HEIGHT), dpi=self.FIGURE_DPI)
        plt.text(0.5, 0.5, f"${formula}$", fontsize=self.FONT_SIZE, ha='center', va='center')
        plt.axis('off')
        plt.savefig(temp_file, bbox_inches='tight', transparent=True, pad_inches=self.FIGURE_PAD)
        plt.close()

        label = QLabel(f"{description}:")
        label.setProperty("class", "formula")
        label.setPixmap(QPixmap(temp_file))
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.temp_files.append(temp_file)
        return label

    def closeEvent(self, event: QDialog.closeEvent) -> None:  # pylint: disable=invalid-name
        """Clean up temporary files when closing the window.

        Args:
            event: The close event.
        """
        for temp_file in self.temp_files:
            try:
                os.remove(temp_file)
            except OSError:
                pass
        event.accept()
