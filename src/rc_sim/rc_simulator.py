"""Module for simulating an RC circuit with a GUI interface."""

import csv
import logging
import os
from typing import Optional, Tuple

# pylint: disable=no-name-in-module
import numpy as np
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QFormLayout, QLineEdit,
    QComboBox, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox,
    QFileDialog, QSlider, QLabel, QDialog, QTextEdit
)

# pylint: disable=import-error
from src.rc_sim.circuit_diagram import CircuitDiagram
from src.rc_sim.help_window import HelpWindow
from src.rc_sim.plot_widget import PlotWidget
from src.rc_sim.rc_calculator import RCCalculator


# pylint: disable=import-error


class PreviewDialog(QDialog):  # pylint: disable=too-few-public-methods
    """Dialog for previewing CSV data."""

    # Constants for dialog geometry
    DIALOG_X: int = 200
    DIALOG_Y: int = 200
    DIALOG_WIDTH: int = 600
    DIALOG_HEIGHT: int = 400

    def __init__(self, data: str, parent: Optional[QDialog] = None) -> None:
        """Initialize the preview dialog.

        Args:
            data: CSV data to display.
            parent: Parent widget (default: None).
        """
        super().__init__(parent)
        self.setWindowTitle("Предварительный просмотр CSV")
        # pylint: disable=duplicate-code
        self.setGeometry(self.DIALOG_X, self.DIALOG_Y,
                         self.DIALOG_WIDTH, self.DIALOG_HEIGHT)
        layout = QVBoxLayout(self)
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setText(data)
        layout.addWidget(self.text_edit)
        close_button = QPushButton("Закрыть")
        close_button.clicked.connect(self.close)
        layout.addWidget(close_button)


class RCSimulator(QMainWindow):  # pylint: disable=too-many-instance-attributes
    """Main window for RC circuit simulation."""

    # Constants for window and UI settings
    WINDOW_X: int = 100
    WINDOW_Y: int = 100
    WINDOW_WIDTH: int = 1200
    WINDOW_HEIGHT: int = 800
    DEFAULT_CAPACITANCE: str = "1"
    DEFAULT_RESISTANCE: str = "1000"
    DEFAULT_EMF: str = "10"
    DEFAULT_INTERNAL_RESISTANCE: str = "0"
    DEFAULT_TEMP_COEFF: str = "0.0001"
    DEFAULT_TEMPERATURE: str = "25"
    DEFAULT_PRECISION: str = "6"
    TIME_STEP: float = 0.00001
    TABLE_ROWS: int = 10
    TABLE_COLUMNS: int = 2
    TABLE_WIDTH: int = 300
    SLIDER_MIN: int = 10
    SLIDER_MAX: int = 200
    SLIDER_DEFAULT: int = 50
    SLIDER_TICK: int = 10
    CSV_MAX_POINTS: int = 1000
    PRECISION_MIN: int = 1
    PRECISION_MAX: int = 12
    PLOT_DPI: int = 300
    STYLESHEET: str = (
        "QMainWindow { background-color: #000000; color: #ffffff; } "
        "QLineEdit { background-color: #333333; color: #ffffff; border: 1px solid #4da8da; } "
        "QPushButton { background-color: #4da8da; color: #ffffff; border: none; padding: 5px; } "
        "QPushButton:hover { background-color: #357abd; } "
        "QComboBox { background-color: #333333; color: #ffffff; } "
        "QTableWidget { background-color: #333333; color: #ffffff; } "
        "QSlider { background-color: #333333; } "
        "QLabel { color: #ffffff; } "
        "QTextEdit { background-color: #333333; color: #ffffff; }"
    )

    def __init__(self) -> None:
        """Initialize the RC simulator window."""
        super().__init__()
        self.setWindowTitle("RC-Sim: Симуляция RC-цепи")
        icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', 'assets',
                                 'app.ico')  # pylint: disable=line-too-long
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        else:
            logging.warning(f"Icon file not found: {icon_path}")  # pylint:disable=logging-fstring-interpolation
        self.setGeometry(self.WINDOW_X, self.WINDOW_Y,
                         self.WINDOW_WIDTH, self.WINDOW_HEIGHT)
        self.calculator = RCCalculator()
        self.plot_widget = PlotWidget()
        self.circuit_diagram = CircuitDiagram()
        self.is_animation_paused: bool = False
        self.setup_ui()

    def setup_ui(self) -> None:
        """Set up the UI for the main window."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        input_widget = QWidget()
        input_layout = QVBoxLayout(input_widget)

        self.setStyleSheet(self.STYLESHEET)

        self.setup_form_layout(input_layout)
        self.setup_buttons(input_layout)
        self.setup_result_table(input_layout)
        main_layout.addWidget(input_widget)
        main_layout.addWidget(self.plot_widget, stretch=1)

    def setup_form_layout(self, input_layout: QVBoxLayout) -> None:
        """Set up the form layout for input fields."""
        form_layout = QFormLayout()
        self.capacitance_input = QLineEdit(self.DEFAULT_CAPACITANCE)  # pylint: disable=attribute-defined-outside-init
        self.resistance_input = QLineEdit(self.DEFAULT_RESISTANCE)  # pylint: disable=attribute-defined-outside-init
        self.voltage_input = QLineEdit(self.DEFAULT_EMF)  # pylint: disable=attribute-defined-outside-init
        # pylint: disable=attribute-defined-outside-init
        self.internal_resistance_input = QLineEdit(
            self.DEFAULT_INTERNAL_RESISTANCE)
        self.source_combo = QComboBox()  # pylint: disable=attribute-defined-outside-init
        self.source_combo.addItems(["DC", "AC"])
        self.mode_combo = QComboBox()  # pylint: disable=attribute-defined-outside-init
        self.mode_combo.addItems(["Зарядка", "Разрядка"])
        self.temp_coeff_input = QLineEdit(self.DEFAULT_TEMP_COEFF)  # pylint: disable=attribute-defined-outside-init
        # pylint: disable=attribute-defined-outside-init
        self.temperature_input = QLineEdit(self.DEFAULT_TEMPERATURE)
        self.export_precision_input = QLineEdit(
            self.DEFAULT_PRECISION)  # pylint: disable=attribute-defined-outside-init
        self.csv_delimiter_combo = QComboBox()  # pylint: disable=attribute-defined-outside-init
        self.csv_delimiter_combo.addItems(["Точка (.)", "Запятая (,)"])

        for input_field in (
                self.capacitance_input,
                self.resistance_input,
                self.voltage_input,
                self.internal_resistance_input,
                self.temp_coeff_input,
                self.temperature_input,
                self.export_precision_input,
        ):
            input_field.textChanged.connect(
                lambda text, field=input_field: self.validate_input_field(field))  # pylint: disable=line-too-long

        form_layout.addRow("Ёмкость (мкФ):", self.capacitance_input)
        form_layout.addRow("Сопротивление (Ом):", self.resistance_input)
        form_layout.addRow("ЭДС (В):", self.voltage_input)
        form_layout.addRow("Внутреннее сопротивление (R_int):", self.internal_resistance_input)
        form_layout.addRow("Тип источника (.:", self.source_combo)
        form_layout.addRow("Режим:", self.mode_combo)
        form_layout.addRow("Температурный коэффициент (1/°C):", self.temp_coeff_input)
        form_layout.addRow("Температура (°C):", self.temperature_input)
        form_layout.addRow("Точность экспорта (знаков):", self.export_precision_input)
        # pylint: disable=attribute-defined-outside-init
        form_layout.addRow("Десятичный разделитель:", self.csv_delimiter_combo)

        # pylint: disable=attribute-defined-outside-init
        self.animation_speed_label = QLabel(
            f"Скорость анимации (мс): {self.SLIDER_DEFAULT}")
        # pylint: disable=attribute-defined-outside-init
        self.animation_speed_slider = QSlider(
            Qt.Orientation.Horizontal)
        self.animation_speed_slider.setMinimum(self.SLIDER_MIN)
        self.animation_speed_slider.setMaximum(self.SLIDER_MAX)
        self.animation_speed_slider.setValue(self.SLIDER_DEFAULT)
        self.animation_speed_slider.setTickInterval(self.SLIDER_TICK)
        self.animation_speed_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.animation_speed_slider.valueChanged.connect(self.update_animation_speed_label)
        form_layout.addRow(self.animation_speed_label, self.animation_speed_slider)

        input_layout.addLayout(form_layout)

    def setup_buttons(self, input_layout: QVBoxLayout) -> None:
        """Set up buttons for the UI."""
        run_button = QPushButton("Запустить симуляцию")
        run_button.clicked.connect(self.run_simulation)
        input_layout.addWidget(run_button)

        self.pause_button = QPushButton("Пауза")  # pylint: disable=attribute-defined-outside-init
        self.pause_button.clicked.connect(self.toggle_animation)
        input_layout.addWidget(self.pause_button)

        preview_button = QPushButton("Предпросмотр CSV")
        preview_button.clicked.connect(self.preview_csv)
        input_layout.addWidget(preview_button)

        export_button = QPushButton("Экспорт в CSV")
        export_button.clicked.connect(self.export_to_csv)
        input_layout.addWidget(export_button)

        save_png_button = QPushButton("Сохранить график в PNG")
        save_png_button.clicked.connect(self.save_plot_to_png)
        input_layout.addWidget(save_png_button)

        help_button = QPushButton("Справка")
        help_button.clicked.connect(self.show_help)
        input_layout.addWidget(help_button)

        exit_button = QPushButton("Выход")
        exit_button.clicked.connect(self.close)
        input_layout.addWidget(exit_button)

        input_layout.addWidget(self.circuit_diagram)

    def setup_result_table(self, input_layout: QVBoxLayout) -> None:
        """Set up the result table."""
        self.result_table = QTableWidget()  # pylint: disable=attribute-defined-outside-init
        self.result_table.setRowCount(self.TABLE_ROWS)
        self.result_table.setColumnCount(self.TABLE_COLUMNS)
        self.result_table.setHorizontalHeaderLabels(["Параметр", "Значение"])
        self.result_table.setFixedWidth(self.TABLE_WIDTH)
        input_layout.addWidget(self.result_table)
        input_layout.addStretch()

    def validate_input_field(self, line_edit: QLineEdit) -> None:
        """Validate input field as a float.

        Args:
            line_edit: QLineEdit widget to validate.
        """
        try:
            float(line_edit.text())
            line_edit.setStyleSheet("border: 1px solid #4da8da;")
        except ValueError:
            line_edit.setStyleSheet("border: 1px solid red;")

    def update_animation_speed_label(self) -> None:
        """Update the animation speed label with the current slider value."""
        self.animation_speed_label.setText(
            f"Скорость анимации (мс): {self.animation_speed_slider.value()}"
        )

    def run_simulation(self) -> None:
        """Run the RC circuit simulation."""
        try:
            capacitance = float(self.capacitance_input.text()) * 1e-6
            resistance = float(self.resistance_input.text())
            emf = float(self.voltage_input.text())
            internal_resistance = float(self.internal_resistance_input.text())
            source_type = self.source_combo.currentText()
            discharge = self.mode_combo.currentText() == "Разрядка"
            alpha = float(self.temp_coeff_input.text())
            temperature = float(self.temperature_input.text())
        except ValueError:
            logging.error("Invalid input parameters")
            QMessageBox.critical(self, "Ошибка", "Введите корректные числовые значения.")
            return

        if not self.calculator.set_parameters(
                capacitance, resistance, emf, source_type, alpha, temperature, internal_resistance
        ):
            QMessageBox.critical(
                self, "Ошибка",
                "Параметры должны быть положительными (внутреннее сопротивление может быть 0)."
            )
            return

        if self.calculator.calculate(time_step=self.TIME_STEP, discharge=discharge):
            logging.debug(
                "Before plotting: time_len=%s, Vc_len=%s, I_len=%s",
                len(self.calculator.time), len(self.calculator.Vc), len(self.calculator.I)
            )
            print(
                f"Time: len={len(self.calculator.time)}, first 5={self.calculator.time[:5]}"
            )
            print(
                f"Vc: len={len(self.calculator.Vc)}, first 5={self.calculator.Vc[:5]}"
            )
            print(
                f"I: len={len(self.calculator.I)}, first 5={self.calculator.I[:5]}"
            )
            self.update_table()
            interval = self.animation_speed_slider.value()
            self.plot_widget.update_plot(
                self.calculator.time,
                self.calculator.Vc,
                self.calculator.I,
                V0=self.calculator.V0,
                animate=True,
                interval=interval,
                circuit_diagram=self.circuit_diagram
            )
            self.is_animation_paused = False
            self.pause_button.setText("Пауза")
            logging.debug("Simulation completed successfully")
        else:
            QMessageBox.critical(self, "Ошибка", "Ошибка в расчётах.")

    def toggle_animation(self) -> None:
        """Toggle the animation pause state."""
        if not hasattr(self.plot_widget, 'anim') or self.plot_widget.anim is None:
            QMessageBox.warning(self, "Предупреждение", "Сначала запустите симуляцию.")
            return

        self.is_animation_paused = not self.is_animation_paused

        if self.is_animation_paused:
            self.plot_widget.anim.event_source.stop()
            self.pause_button.setText("Возобновить")
        else:
            self.plot_widget.anim.event_source.start()
            self.plot_widget.canvas.flush_events()
            self.pause_button.setText("Пауза")

    def save_plot_to_png(self) -> None:
        """Save the current plot to a PNG file."""
        if not hasattr(self.plot_widget, 'time') or not self.plot_widget.time.size:
            QMessageBox.warning(self, "Предупреждение", "Сначала запустите симуляцию.")
            return
        try:
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Сохранить график",
                os.path.expanduser("~/rc_plot.png"), "PNG Files (*.png)"
            )

            if file_path:
                self.plot_widget.fig.savefig(file_path, dpi=self.PLOT_DPI, bbox_inches='tight')
                QMessageBox.information(self, "Успех", f"График сохранён в {file_path}")
        except OSError as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при сохранении графика: {str(e)}")

    def get_csv_data(self) -> Tuple[Optional[str], Optional[str]]:
        """Generate CSV data from simulation results.

        Returns:
            Tuple of (CSV data string, error message). If successful, error is None.
        """
        if not hasattr(self.calculator, 'time') or self.calculator.time is None:
            return None, "Сначала запустите симуляцию."

        try:
            precision = int(self.export_precision_input.text())

            if precision < self.PRECISION_MIN or precision > self.PRECISION_MAX:
                raise ValueError(
                    f"Точность должна быть от {self.PRECISION_MIN} до {self.PRECISION_MAX}")  # pylint: disable=line-too-long

            delimiter = ',' if self.csv_delimiter_combo.currentText() == "Запятая (,)" else '.'

            num_points = min(self.CSV_MAX_POINTS, len(self.calculator.time))
            indices = np.linspace(0, len(self.calculator.time) - 1, num_points, dtype=int)
            logging.debug("CSV data: num_points=%s, indices_len=%s", num_points, len(indices))

            data = ['Время (с);Напряжение (В);Ток (А)']
            for idx in indices:
                time_str = (
                    f"{self.calculator.time[idx]:.{precision}f}"
                    .rstrip('0').rstrip('.').replace('.', delimiter)
                )
                vc_str = (
                    f"{self.calculator.Vc[idx]:.{precision}f}"
                    .rstrip('0').rstrip('.').replace('.', delimiter)
                )
                i_str = (
                    f"{self.calculator.I[idx]:.{precision}f}"
                    .rstrip('0').rstrip('.').replace('.', delimiter)
                )
                data.append(f"{time_str};{vc_str};{i_str}")

            return '\n'.join(data), None
        except ValueError as e:
            return None, str(e)

    def preview_csv(self) -> None:
        """Show a preview of the CSV data."""
        data, error = self.get_csv_data()

        if error:
            QMessageBox.critical(self, "Ошибка", error)
            return

        preview_dialog = PreviewDialog(data, self)
        preview_dialog.exec()

    def export_to_csv(self) -> None:
        """Export simulation data to a CSV file."""
        if not hasattr(self.calculator, 'time') or self.calculator.time is None:
            QMessageBox.warning(self, "Предупреждение", "Сначала запустите симуляцию.")
            return

        try:
            precision = int(self.export_precision_input.text())

            if precision < self.PRECISION_MIN or precision > self.PRECISION_MAX:
                raise ValueError(
                    f"Точность должна быть от {self.PRECISION_MIN} до {self.PRECISION_MAX}")  # pylint: disable=line-too-long

            delimiter = ',' if self.csv_delimiter_combo.currentText() == "Запятая (,)" else '.'

            file_path, _ = QFileDialog.getSaveFileName(
                self, "Сохранить CSV",
                os.path.expanduser("~/rc_simulation.csv"), "CSV Files (*.csv)"
            )

            if file_path:
                num_points = min(self.CSV_MAX_POINTS, len(self.calculator.time))
                indices = np.linspace(0, len(self.calculator.time) - 1, num_points, dtype=int)
                logging.debug("Export: num_points=%s, indices_len=%s", num_points, len(indices))

                with open(file_path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f, delimiter=';')
                    writer.writerow(['Время (с)', 'Напряжение (В)', 'Ток (А)'])
                    for idx in indices:
                        time_str = (
                            f"{self.calculator.time[idx]:.{precision}f}"
                            .rstrip('0').rstrip('.').replace('.', delimiter)
                        )
                        vc_str = (
                            f"{self.calculator.Vc[idx]:.{precision}f}"
                            .rstrip('0').rstrip('.').replace('.', delimiter)
                        )
                        i_str = (
                            f"{self.calculator.I[idx]:.{precision}f}"
                            .rstrip('0').rstrip('.').replace('.', delimiter)
                        )
                        writer.writerow([time_str, vc_str, i_str])

                QMessageBox.information(
                    self, "Успех", f"Экспортировано {len(indices)} точек в {file_path}"
                )
        except ValueError as e:
            logging.error("Input error: %s", str(e))
            QMessageBox.critical(self, "Ошибка", str(e))
        except OSError as e:
            logging.error("Export error: %s", str(e))
            QMessageBox.critical(self, "Ошибка", f"Ошибка при экспорте: {str(e)}")

    def show_help(self) -> None:
        """Show the help window."""
        help_window = HelpWindow(self)
        help_window.exec()

    def update_table(self) -> None:
        """Update the result table with simulation parameters."""
        params = [
            ("Ёмкость (мкФ)", f"{self.calculator.C * 1e6:.2f}"),
            ("Сопротивление (Ом)", f"{self.calculator.R:.2f}"),
            ("Внутреннее сопротивление (Ом)", f"{self.calculator.R_int:.2f}"),
            ("ЭДС (В)", f"{self.calculator.V0:.2f}"),
            ("Тип источника", self.calculator.source_type),
            ("Темп. коэфф. (1/°C)", f"{self.calculator.alpha:.6f}"),
            ("Температура (°C)", f"{self.calculator.temperature:.2f}"),
            ("Энергия (Дж)", f"{self.calculator.energy:.6f}"),
            ("Тепловые потери (Вт)", f"{self.calculator.power_loss:.6f}"),
            ("Постоянная времени (с)", f"{self.calculator.tau:.6f}"),
        ]

        self.result_table.setRowCount(len(params))
        for row, (param, value) in enumerate(params):
            self.result_table.setItem(row, 0, QTableWidgetItem(param))
            self.result_table.setItem(row, 1, QTableWidgetItem(value))
        self.result_table.resizeColumnsToContents()
