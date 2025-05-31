from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QScrollArea, QWidget
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
import matplotlib.pyplot as plt
import os
import tempfile
import uuid


class HelpWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Справка: RC-цепь")
        self.setGeometry(200, 200, 700, 500)
        self.temp_files = []
        self.setup_ui()


    def setup_ui(self):
        layout = QVBoxLayout(self)
        container = QWidget()
        container_layout = QVBoxLayout(container)

        self.setStyleSheet("""
            QDialog { background-color: #000000; color: #ffffff; }
            QLabel { color: #ffffff; font-size: 16px; font-family: Arial; }
            QLabel.header { color: #4da8da; font-size: 20px; font-weight: bold; margin: 10px 0; }
            QLabel.formula { margin: 10px 0; }
        """)

        title_label = QLabel("Справочная информация по RC-цепи")
        title_label.setProperty("class", "header")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        container_layout.addWidget(title_label)

        description = QLabel("""
        Это приложение моделирует поведение RC-цепи (резистор-конденсатор) при постоянном (DC) или переменном (AC) напряжении.
        Основные параметры:
        - Ёмкость (C): в микрофарадах (мкФ).
        - Сопротивление (R): в омах (Ом).
        - Напряжение (V₀): амплитуда источника (В).
        - Температурный коэффициент (α): влияет на сопротивление при изменении температуры.
        - Температура (T): влияет на сопротивление через формулу R = R₀(1 + α(T - 25)).
        """)
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
            (r"V_C(t) = V_0 \left(1 - e^{-t / \tau}\right)", "Напряжение на конденсаторе"),
            (r"I(t) = \frac{V_0}{R} e^{-t / \tau}", "Ток"),
            (r"\tau = R \cdot C", "Постоянная времени")
        ]

        for formula, desc in dc_formulas:
            container_layout.addWidget(self.create_formula_label(formula, desc))

        ac_label = QLabel("Для переменного тока (AC):")
        ac_label.setProperty("class", "header")
        ac_label.setStyleSheet("font-size: 16px; color: #4da8da;")
        container_layout.addWidget(ac_label)

        ac_formulas = [
            (r"Z = \sqrt{R^2 + \frac{1}{(\omega C)^2}}", "Импеданс"),
            (r"V_C(t) = \frac{V_0 \sin(\omega t)}{\sqrt{1 + (\omega R C)^2}}", "Напряжение"),
            (r"I(t) = \frac{V_0}{Z} \sin\left(\omega t - \arctan\left(\frac{1}{\omega R C}\right)\right)", "Ток")
        ]

        for formula, desc in ac_formulas:
            container_layout.addWidget(self.create_formula_label(formula, desc))

        energy_label = QLabel("Энергетические характеристики:")
        energy_label.setProperty("class", "header")
        energy_label.setStyleSheet("font-size: 16px; color: #4da8da;")
        container_layout.addWidget(energy_label)

        energy_formulas = [
            (r"E = \frac{1}{2} C V_C^2", "Энергия конденсатора"),
            (r"P = \text{mean}(I^2 R)", "Тепловые потери")
        ]

        for formula, desc in energy_formulas:
            container_layout.addWidget(self.create_formula_label(formula, desc))

        container_layout.addStretch()
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(container)
        layout.addWidget(scroll_area)


    def create_formula_label(self, formula, description):
        temp_file = os.path.join(tempfile.gettempdir(), f"formula_{uuid.uuid4()}.png")
        plt.figure(figsize=(4, 1), dpi=100)
        plt.text(0.5, 0.5, f"${formula}$", fontsize=14, ha='center', va='center')
        plt.axis('off')
        plt.savefig(temp_file, bbox_inches='tight', transparent=True, pad_inches=0.1)
        plt.close()

        label = QLabel(f"{description}:")
        label.setProperty("class", "formula")
        label.setPixmap(QPixmap(temp_file))
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.temp_files.append(temp_file)
        return label

    def closeEvent(self, event):
        for temp_file in self.temp_files:
            try:
                os.remove(temp_file)
            except OSError:
                pass

        event.accept()
