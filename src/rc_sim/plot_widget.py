"""Widget for plotting RC circuit simulation results."""

import logging
from typing import Optional
import matplotlib.pyplot as plt
import numpy as np
from PyQt6.QtWidgets import QWidget, QVBoxLayout    # pylint: disable=no-name-in-module
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.animation import FuncAnimation


class PlotWidget(QWidget):  # pylint: disable=too-many-instance-attributes
    """Widget for displaying voltage and current plots of an RC circuit simulation."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """Initialize the plot widget."""
        super().__init__(parent)
        self.fig, (self.ax1, self.ax2) = plt.subplots(2, 1, figsize=(6, 6))
        self.canvas = FigureCanvas(self.fig)
        layout = QVBoxLayout(self)
        layout.addWidget(self.canvas)

        self.line1, = self.ax1.plot([], [], label='Напряжение (В)', color='blue')
        self.line2, = self.ax2.plot([], [], label='Ток (А)', color='red')
        self.setup_axes()
        self.anim = None
        self.time = []
        self.voltage_c = []
        self.current = []
        self.emf = 10

    def setup_axes(self) -> None:
        """Configure the plot axes with labels, titles, and grid."""
        self.ax1.set_title('Зарядка/Разрядка конденсатора')
        self.ax1.set_xlabel('Время (с)')
        self.ax1.set_ylabel('Напряжение (В)')
        self.ax2.set_xlabel('Время (с)')
        self.ax2.set_ylabel('Ток (А)')
        self.ax1.legend()
        self.ax2.legend()
        self.ax1.grid(True)
        self.ax2.grid(True)
        self.fig.tight_layout()

    def update_plot(self, time, voltage_c, current, emf=10, animate=True, interval=50, circuit_diagram=None) -> None:   # pylint: disable=line-too-long,too-many-arguments,too-many-positional-arguments
        """Update the plot with new simulation data.

        Args:
            time: Time array for the plot.
            voltage_c: Voltage across the capacitor.
            current: Current through the circuit.
            emf: Electromotive force (default: 10).
            animate: Whether to animate the plot (default: True).
            interval: Animation interval in milliseconds (default: 50).
            circuit_diagram: Optional circuit diagram object to update during animation.
        """
        try:
            if not all(isinstance(arr, (list, np.ndarray)) for arr in [time, voltage_c, current]):
                raise ValueError("Входные данные должны быть списком или numpy массивом")
            if not all(len(arr) > 0 for arr in [time, voltage_c, current]):
                raise ValueError("Входные данные пусты")
            if not all(np.isfinite(arr).all() for arr in [time, voltage_c, current]):
                raise ValueError("Данные содержат нечисловые значения")

            logging.debug(
                "Данные для графика: time_len=%s, voltage_c_len=%s, current_len=%s",
                len(time), len(voltage_c), len(current)
            )
            logging.debug(
                "Пример данных: time=%s, voltage_c=%s, current=%s",
                time[:5], voltage_c[:5], current[:5]
            )

            self.time = np.array(time)
            self.voltage_c = np.array(voltage_c)
            self.current = np.array(current)
            self.emf = emf

            self.reset_plot()
            self.update_axes_limits()

            if animate:
                self.setup_animation(interval, circuit_diagram)

            self.canvas.draw()
            self.canvas.flush_events()
            logging.debug("График отрисован")
        except (ValueError, TypeError) as e:
            logging.error("Ошибка при обновлении графика: %s", str(e))
            self.reset_plot()
            self.canvas.draw()

    def reset_plot(self) -> None:
        """Reset the plot by clearing axes and reinitializing lines."""
        if self.anim is not None:
            self.anim.event_source.stop()
            self.anim = None

        self.ax1.clear()
        self.ax2.clear()
        self.line1, = self.ax1.plot([], [], label='Напряжение (В)', color='blue')
        self.line2, = self.ax2.plot([], [], label='Ток (А)', color='red')
        self.setup_axes()

        self.line1.set_data(self.time, self.voltage_c)
        self.line2.set_data(self.time, self.current)

    def update_axes_limits(self) -> None:
        """Update the axes limits based on the data."""
        max_time = max(self.time) if max(self.time) > 0 else 1
        self.ax1.set_xlim(0, max_time)
        self.ax2.set_xlim(0, max_time)

        v_min, v_max = min(self.voltage_c), max(self.voltage_c)
        i_min, i_max = min(self.current), max(self.current)
        v_margin = (v_max - v_min) * 0.1 or 0.1
        i_margin = (i_max - i_min) * 0.1 or 0.1
        self.ax1.set_ylim(v_min - v_margin, v_max + v_margin)
        self.ax2.set_ylim(i_min - i_margin, i_max + i_margin)

    def setup_animation(self, interval: int, circuit_diagram: Optional[object]) -> None:
        """Set up the animation for the plot.

        Args:
            interval: Animation interval in milliseconds.
            circuit_diagram: Optional circuit diagram object to update during animation.
        """
        def init():
            logging.debug("Инициализация анимации")
            self.line1.set_data([], [])
            self.line2.set_data([], [])

            if circuit_diagram:
                circuit_diagram.set_charge_level(0, self.emf)

            return self.line1, self.line2

        def update(frame):
            logging.debug("Обновление кадра %s", frame)
            self.line1.set_data(self.time[:frame], self.voltage_c[:frame])
            self.line2.set_data(self.time[:frame], self.current[:frame])

            if circuit_diagram:
                circuit_diagram.set_charge_level(
                    self.voltage_c[frame-1] if frame > 0 else 0, self.emf
                )

            self.canvas.flush_events()
            return self.line1, self.line2

        self.anim = FuncAnimation(
            self.fig,
            update,
            init_func=init,
            frames=len(self.time),
            interval=interval,
            blit=True
        )
