from PyQt6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QFormLayout, QLineEdit, QComboBox, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox, QFileDialog, QSlider, QLabel, QDialog, QTextEdit
from PyQt6.QtCore import Qt
from rc_calculator import RCCalculator
from plot_widget import PlotWidget
from circuit_diagram import CircuitDiagram
from help_window import HelpWindow
import csv
import numpy as np
import logging
import os

class PreviewDialog(QDialog):
    def __init__(self, data, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Предварительный просмотр CSV")
        self.setGeometry(200, 200, 600, 400)
        layout = QVBoxLayout(self)
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setText(data)
        layout.addWidget(self.text_edit)
        close_button = QPushButton("Закрыть")
        close_button.clicked.connect(self.close)
        layout.addWidget(close_button)

class RCSimulator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("RC-Sim: Симуляция RC-цепи")
        self.setGeometry(100, 100, 1200, 800)
        self.calculator = RCCalculator()
        self.plot_widget = PlotWidget()
        self.circuit_diagram = CircuitDiagram()
        self.is_animation_paused = False
        self.setup_ui()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        input_widget = QWidget()
        input_layout = QVBoxLayout(input_widget)

        self.setStyleSheet("""
            QMainWindow { background-color: #000000; color: #ffffff; }
            QLineEdit { background-color: #333333; color: #ffffff; border: 1px solid #4da8da; }
            QPushButton { background-color: #4da8da; color: #ffffff; border: none; padding: 5px; }
            QPushButton:hover { background-color: #357abd; }
            QComboBox { background-color: #333333; color: #ffffff; }
            QTableWidget { background-color: #333333; color: #ffffff; }
            QSlider { background-color: #333333; }
            QLabel { color: #ffffff; }
            QTextEdit { background-color: #333333; color: #ffffff; }
        """)

        form_layout = QFormLayout()
        self.capacitance_input = QLineEdit("1")
        self.resistance_input = QLineEdit("1000")
        self.voltage_input = QLineEdit("10")
        self.source_combo = QComboBox()
        self.source_combo.addItems(["DC", "AC"])
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["Зарядка", "Разрядка"])
        self.temp_coeff_input = QLineEdit("0.0001")
        self.temperature_input = QLineEdit("25")
        self.export_precision_input = QLineEdit("6")
        self.csv_delimiter_combo = QComboBox()
        self.csv_delimiter_combo.addItems(["Точка (.)", "Запятая (,)"])

        for input_field in [self.capacitance_input, self.resistance_input, self.voltage_input, self.temp_coeff_input, self.temperature_input, self.export_precision_input]:
            input_field.textChanged.connect(lambda: self.validate_input(input_field))

        form_layout.addRow("Ёмкость (мкФ):", self.capacitance_input)
        form_layout.addRow("Сопротивление (Ом):", self.resistance_input)
        form_layout.addRow("Напряжение (В):", self.voltage_input)
        form_layout.addRow("Тип источника:", self.source_combo)
        form_layout.addRow("Режим:", self.mode_combo)
        form_layout.addRow("Темп. коэфф. (1/°C):", self.temp_coeff_input)
        form_layout.addRow("Температура (°C):", self.temperature_input)
        form_layout.addRow("Точность экспорта (знаков):", self.export_precision_input)
        form_layout.addRow("Десятичный разделитель:", self.csv_delimiter_combo)

        # Ползунок скорости анимации
        self.animation_speed_label = QLabel("Скорость анимации (мс): 50")
        self.animation_speed_slider = QSlider(Qt.Orientation.Horizontal)
        self.animation_speed_slider.setMinimum(10)
        self.animation_speed_slider.setMaximum(200)
        self.animation_speed_slider.setValue(50)
        self.animation_speed_slider.setTickInterval(10)
        self.animation_speed_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.animation_speed_slider.valueChanged.connect(self.update_animation_speed_label)
        form_layout.addRow(self.animation_speed_label, self.animation_speed_slider)

        input_layout.addLayout(form_layout)

        run_button = QPushButton("Запустить симуляцию")
        run_button.clicked.connect(self.run_simulation)
        input_layout.addWidget(run_button)

        self.pause_button = QPushButton("Пауза")
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

        self.result_table = QTableWidget()
        self.result_table.setRowCount(9)
        self.result_table.setColumnCount(2)
        self.result_table.setHorizontalHeaderLabels(["Параметр", "Значение"])
        self.result_table.setFixedWidth(300)
        input_layout.addWidget(self.result_table)
        input_layout.addStretch()

        main_layout.addWidget(input_widget)
        main_layout.addWidget(self.plot_widget, stretch=1)

    def validate_input(self, line_edit):
        try:
            float(line_edit.text())
            line_edit.setStyleSheet("border: 1px solid #4da8da;")
        except ValueError:
            line_edit.setStyleSheet("border: 1px solid red;")

    def update_animation_speed_label(self):
        self.animation_speed_label.setText(f"Скорость анимации (мс): {self.animation_speed_slider.value()}")

    def run_simulation(self):
        try:
            C = float(self.capacitance_input.text()) * 1e-6
            R = float(self.resistance_input.text())
            V0 = float(self.voltage_input.text())
            source_type = self.source_combo.currentText()
            discharge = self.mode_combo.currentText() == "Разрядка"
            alpha = float(self.temp_coeff_input.text())
            temperature = float(self.temperature_input.text())
        except ValueError:
            logging.error("Некорректные входные параметры")
            QMessageBox.critical(self, "Ошибка", "Введите корректные числовые значения.")
            return

        if not self.calculator.set_parameters(C, R, V0, source_type, alpha, temperature):
            QMessageBox.critical(self, "Ошибка", "Параметры должны быть положительными.")
            return

        if self.calculator.calculate(time_step=0.00001, discharge=discharge):
            logging.debug(f"Перед отрисовкой: time_len={len(self.calculator.time)}, Vc_len={len(self.calculator.Vc)}, I_len={len(self.calculator.I)}")
            print(f"Time: len={len(self.calculator.time)}, first 5={self.calculator.time[:5]}")
            print(f"Vc: len={len(self.calculator.Vc)}, first 5={self.calculator.Vc[:5]}")
            print(f"I: len={len(self.calculator.I)}, first 5={self.calculator.I[:5]}")
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
            logging.debug("Симуляция успешно выполнена")
        else:
            QMessageBox.critical(self, "Ошибка", "Ошибка в расчётах.")

    def toggle_animation(self):
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

    def save_plot_to_png(self):
        if not hasattr(self.plot_widget, 'time') or not self.plot_widget.time.size:
            QMessageBox.warning(self, "Предупреждение", "Сначала запустите симуляцию.")
            return
        try:
            file_path, _ = QFileDialog.getSaveFileName(self, "Сохранить график", os.path.expanduser("~/rc_plot.png"), "PNG Files (*.png)")
            if file_path:
                self.plot_widget.fig.savefig(file_path, dpi=300, bbox_inches='tight')
                QMessageBox.information(self, "Успех", f"График сохранён в {file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при сохранении графика: {str(e)}")

    def get_csv_data(self):
        if not hasattr(self.calculator, 'time') or self.calculator.time is None:
            return None, "Сначала запустите симуляцию."
        try:
            precision = int(self.export_precision_input.text())
            if precision < 1 or precision > 12:
                raise ValueError("Точность должна быть от 1 до 12")
            delimiter = ',' if self.csv_delimiter_combo.currentText() == "Запятая (,)" else '.'

            num_points = min(1000, len(self.calculator.time))
            indices = np.linspace(0, len(self.calculator.time)-1, num_points, dtype=int)
            logging.debug(f"CSV данные: num_points={num_points}, indices_len={len(indices)}")

            data = ['Время (с);Напряжение (В);Ток (А)']
            for idx in indices:
                time_str = f"{self.calculator.time[idx]:.{precision}f}".rstrip('0').rstrip('.').replace('.', delimiter)
                vc_str = f"{self.calculator.Vc[idx]:.{precision}f}".rstrip('0').rstrip('.').replace('.', delimiter)
                i_str = f"{self.calculator.I[idx]:.{precision}f}".rstrip('0').rstrip('.').replace('.', delimiter)
                data.append(f"{time_str};{vc_str};{i_str}")

            return '\n'.join(data), None
        except ValueError as e:
            return None, str(e)
        except Exception as e:
            return None, f"Ошибка: {str(e)}"

    def preview_csv(self):
        data, error = self.get_csv_data()
        if error:
            QMessageBox.critical(self, "Ошибка", error)
            return
        preview_dialog = PreviewDialog(data, self)
        preview_dialog.exec()

    def export_to_csv(self):
        if not hasattr(self.calculator, 'time') or self.calculator.time is None:
            QMessageBox.warning(self, "Предупреждение", "Сначала запустите симуляцию.")
            return
        try:
            precision = int(self.export_precision_input.text())
            if precision < 1 or precision > 12:
                raise ValueError("Точность должна быть от 1 до 12")
            delimiter = ',' if self.csv_delimiter_combo.currentText() == "Запятая (,)" else '.'

            file_path, _ = QFileDialog.getSaveFileName(self, "Сохранить CSV", os.path.expanduser("~/rc_simulation.csv"), "CSV Files (*.csv)")
            if file_path:
                num_points = min(1000, len(self.calculator.time))
                indices = np.linspace(0, len(self.calculator.time)-1, num_points, dtype=int)
                logging.debug(f"Экспорт: num_points={num_points}, indices_len={len(indices)}")

                with open(file_path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f, delimiter=';')
                    writer.writerow(['Время (с)', 'Напряжение (В)', 'Ток (А)'])
                    for idx in indices:
                        time_str = f"{self.calculator.time[idx]:.{precision}f}".rstrip('0').rstrip('.').replace('.', delimiter)
                        vc_str = f"{self.calculator.Vc[idx]:.{precision}f}".rstrip('0').rstrip('.').replace('.', delimiter)
                        i_str = f"{self.calculator.I[idx]:.{precision}f}".rstrip('0').rstrip('.').replace('.', delimiter)
                        writer.writerow([time_str, vc_str, i_str])

                QMessageBox.information(self, "Успех", f"Экспортировано {len(indices)} точек в {file_path}")
        except ValueError as e:
            logging.error(f"Ошибка ввода: {str(e)}")
            QMessageBox.critical(self, "Ошибка", str(e))
        except Exception as e:
            logging.error(f"Ошибка при экспорте: {str(e)}")
            QMessageBox.critical(self, "Ошибка", f"Ошибка при экспорте: {str(e)}")

    def show_help(self):
        help_window = HelpWindow(self)
        help_window.exec()

    def update_table(self):
        params = [
            ("Ёмкость (мкФ)", f"{self.calculator.C * 1e6:.2f}"),
            ("Сопротивление (Ом)", f"{self.calculator.R:.2f}"),
            ("Напряжение (В)", f"{self.calculator.V0:.2f}"),
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