"""Module for displaying a help window with RC circuit information and equations."""

import os
import tempfile
import uuid
from typing import Optional
import matplotlib.pyplot as plt
# pylint: disable=no-name-in-module
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QScrollArea, QWidget, QPushButton
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt


class HelpWindow(QDialog):
    """Dialog window to display RC circuit information and equations."""

    WINDOW_X: int = 200
    WINDOW_Y: int = 200
    WINDOW_WIDTH: int = 700
    WINDOW_HEIGHT: int = 500
    FIGURE_WIDTH: float = 5.0
    FIGURE_HEIGHT: float = 1.5
    FIGURE_DPI: int = 150
    FIGURE_PAD: float = 0.2
    FONT_SIZE: int = 18
    STYLESHEET: str = (
        "QDialog { background-color: #212529; color: #F8F9FA; } "
        "QLabel { color: #F8F9FA; font-size: 16px; font-family: Arial; margin: 5px 0; } "
        "QLabel.header { color: #4D8CFF; font-size: 20px; font-weight: bold; margin: 15px 0; } "
        "QLabel.formula { color: #E9ECEF; font-size: 14px; margin: 10px 0; } "
        "QLabel.formula-desc { color: #CED4DA; font-size: 12px; margin: 5px 0 15px 0; } "
        "QPushButton { background-color: #4D8CFF; color: #F8F9FA; font-size: 16px; "
        "border: none; padding: 10px; margin: 15px 0; border-radius: 5px; } "
        "QPushButton:hover { background-color: #3B6CCF; } "
        "QScrollArea { background-color: #495057; border: none; } "
        "QScrollBar:vertical { background: #495057; width: 12px; } "
        "QScrollBar::handle:vertical { background: #4D8CFF; border-radius: 6px; } "
        "QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { background: none; }"
    )
    DESCRIPTION_TEXT: str = (
        "Это приложение моделирует поведение RC-цепи (резистор-конденсатор) при "
        "постоянном (DC) или переменном (AC) напряжении с учётом неидеального источника "
        "питания. RC-цепь состоит из резистора и конденсатора, соединённых последовательно, "
        "и используется в электронике для фильтрации сигналов, создания таймеров и в других "
        "приложениях.\n\n"
        "Основные параметры:\n"
        "- Ёмкость (C): в микрофарадах (мкФ), определяет способность конденсатора накапливать заряд.\n" # pylint: disable=line-too-long
        "- Сопротивление (R): в омах (Ом), ограничивает ток в цепи.\n"
        "- Внутреннее сопротивление источника (R_int): в омах (Ом), моделирует потери источника питания.\n" # pylint: disable=line-too-long
        "- ЭДС (E): амплитуда источника в вольтах (В).\n"
        "- Температурный коэффициент (α): влияет на сопротивление при изменении температуры.\n"
        "- Температура (T): влияет на общее сопротивление по формуле "
        "R_total = (R + R_int)(1 + α(T - 25)).\n\n"
        "Постоянная времени (τ) определяет скорость зарядки/разрядки конденсатора и рассчитывается "
        "как τ = (R + R_int) · C. Чем больше τ, тем медленнее изменяется напряжение на конденсаторе.\n\n"   # pylint: disable=line-too-long
        "Обозначения в формулах:\n"
        "- V_C: Напряжение на конденсаторе (В).\n"
        "- E: Электродвижущая сила источника (В).\n"
        "- I: Ток в цепи (А).\n"
        "- R: Сопротивление резистора (Ом).\n"
        "- R_int: Внутреннее сопротивление источника (Ом).\n"
        "- C: Ёмкость конденсатора (Ф).\n"
        "- τ: Постоянная времени (с).\n"
        "- ω: Угловая частота переменного тока (рад/с).\n"
        "- Z: Импеданс цепи (Ом)."
    )

    def __init__(self, parent: Optional[QDialog] = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Справка: RC-цепь")
        self.setGeometry(self.WINDOW_X, self.WINDOW_Y,
                         self.WINDOW_WIDTH, self.WINDOW_HEIGHT)
        self.temp_files: list[str] = []
        self.setup_ui()

    def setup_ui(self) -> None:
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

        self.add_dc_formulas(container_layout)
        self.add_ac_formulas(container_layout)
        self.add_energy_formulas(container_layout)

        close_button = QPushButton("Закрыть")
        close_button.clicked.connect(self.close)
        container_layout.addWidget(close_button)

        container_layout.addStretch()
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(container)
        layout.addWidget(scroll_area)

    def add_dc_formulas(self, container_layout: QVBoxLayout) -> None:
        dc_label = QLabel("Для постоянного тока (DC):")
        dc_label.setProperty("class", "header")
        dc_label.setStyleSheet("font-size: 16px; color: #4D8CFF;")
        container_layout.addWidget(dc_label)

        dc_formulas = [
            (
                r"V_C(t) = E \left(1 - e^{-t / \tau}\right)",
                "Напряжение на конденсаторе (зарядка)",
                "V_C: напряжение на конденсаторе, E: ЭДС, t: время, τ: постоянная времени."
            ),
            (
                r"V_C(t) = E e^{-t / \tau}",
                "Напряжение на конденсаторе (разрядка)",
                "V_C: напряжение на конденсаторе, E: начальное напряжение, t: время, τ: постоянная времени."    # pylint: disable=line-too-long
            ),
            (
                r"I(t) = \frac{E}{R + R_{\text{int}}} e^{-t / \tau}",
                "Ток (зарядка)",
                "I: ток, E: ЭДС, R: сопротивление, R_int: внутреннее сопротивление, t: время, τ: постоянная времени."   # pylint: disable=line-too-long
            ),
            (
                r"\tau = (R + R_{\text{int}}) \cdot C",
                "Постоянная времени",
                "τ: постоянная времени, R: сопротивление, R_int: внутреннее сопротивление, C: ёмкость." # pylint: disable=line-too-long
            )
        ]

        for formula, desc, components in dc_formulas:
            container_layout.addWidget(self.create_formula_label(formula, desc, components))

    def add_ac_formulas(self, container_layout: QVBoxLayout) -> None:
        ac_label = QLabel("Для переменного тока (AC):")
        ac_label.setProperty("class", "header")
        ac_label.setStyleSheet("font-size: 16px; color: #4D8CFF;")
        container_layout.addWidget(ac_label)

        ac_formulas = [
            (
                r"Z = \sqrt{(R + R_{\text{int}})^2 + \frac{1}{(\omega C)^2}}",
                "Импеданс",
                "Z: импеданс, R: сопротивление, R_int: внутреннее сопротивление, ω: угловая частота, C: ёмкость."   # pylint: disable=line-too-long
            ),
            (
                r"V_C(t) = \frac{E \sin(\omega t)}{\sqrt{1 + (\omega (R + R_{\text{int}}) C)^2}}",
                "Напряжение",
                "V_C: напряжение на конденсаторе, E: амплитуда ЭДС, ω: угловая частота, t: время, "
                "R: сопротивление, R_int: внутреннее сопротивление, C: ёмкость."
            ),
            (
                r"I(t) = \frac{E}{Z} \sin\left(\omega t - \arctan\left(\frac{1}{\omega (R + R_{\text{int}}) C}\right)\right)",  # pylint: disable=line-too-long
                "Ток",
                "I: ток, E: амплитуда ЭДС, Z: импеданс, ω: угловая частота, t: время, "
                "R: сопротивление, R_int: внутреннее сопротивление, C: ёмкость."
            ),
        ]

        for formula, desc, components in ac_formulas:
            container_layout.addWidget(self.create_formula_label(formula, desc, components))

    def add_energy_formulas(self, container_layout: QVBoxLayout) -> None:
        energy_label = QLabel("Энергетические характеристики:")
        energy_label.setProperty("class", "header")
        energy_label.setStyleSheet("font-size: 16px; color: #4D8CFF;")
        container_layout.addWidget(energy_label)

        energy_formulas = [
            (
                r"E = \frac{1}{2} C V_C^2",
                "Энергия конденсатора",
                "E: энергия, C: ёмкость, V_C: напряжение на конденсаторе."
            ),
            (
                r"P = \text{mean}(I^2 (R + R_{\text{int}}))",
                "Тепловые потери",
                "P: мощность потерь, I: ток, R: сопротивление, R_int: внутреннее сопротивление."
            )
        ]

        for formula, desc, components in energy_formulas:
            container_layout.addWidget(self.create_formula_label(formula, desc, components))

    def create_formula_label(self, formula: str, description: str, components: str) -> QLabel:
        temp_file = os.path.join(tempfile.gettempdir(), f"formula_{uuid.uuid4()}.png")
        plt.figure(figsize=(self.FIGURE_WIDTH, self.FIGURE_HEIGHT), dpi=self.FIGURE_DPI)
        plt.text(0.5, 0.5, f"${formula}$", fontsize=self.FONT_SIZE, ha='center', va='center', color='#4D8CFF')  # pylint: disable=line-too-long
        plt.axis('off')
        plt.savefig(temp_file, bbox_inches='tight', transparent=True, pad_inches=self.FIGURE_PAD)
        plt.close()

        label = QLabel(f"{description}:")
        label.setProperty("class", "formula")
        label.setPixmap(QPixmap(temp_file))
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        components_label = QLabel(components)
        components_label.setProperty("class", "formula-desc")
        components_label.setWordWrap(True)
        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.addWidget(label)
        container_layout.addWidget(components_label)
        container_layout.setContentsMargins(0, 0, 0, 0)
        self.temp_files.append(temp_file)
        return container

    def closeEvent(self, event: QDialog.closeEvent) -> None:    # pylint: disable=invalid-name
        for temp_file in self.temp_files:
            if os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except OSError:
                    pass
        event.accept()
