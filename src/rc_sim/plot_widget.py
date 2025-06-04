"""Module for displaying voltage and current plots for RC circuit simulation."""

import logging
from PyQt6.QtWidgets import QWidget, QVBoxLayout  # pylint: disable=no-name-in-module
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.animation import FuncAnimation
import numpy as np


class PlotWidget(QWidget):  # pylint: disable=too-many-instance-attributes
    """Widget for plotting voltage and current over time in an RC circuit simulation."""

    def __init__(self, parent=None):
        """Initialize the PlotWidget with matplotlib figure and canvas.

        Args:
            parent: Parent widget, defaults to None.
        """
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
        self.Vc = []    # pylint: disable=invalid-name
        self.I = []     # pylint: disable=invalid-name
        self.V0 = 10    # pylint: disable=invalid-name

    def setup_axes(self):
        """Configure the appearance and settings of the plot axes."""
        self.fig.patch.set_facecolor("#1e1e1e")
        self.ax1.set_facecolor("#1e1e1e")
        self.ax2.set_facecolor("#1e1e1e")
        self.ax1.set_xlabel('Время (с)', color="white")
        self.ax1.set_ylabel('Напряжение (В)', color="white")
        self.ax2.set_xlabel('Время (с)', color="white")
        self.ax2.set_ylabel('Ток (А)', color="white")
        for ax in [self.ax1, self.ax2]:
            ax.tick_params(colors='white')
            ax.yaxis.label.set_color('white')
            ax.xaxis.label.set_color('white')
            ax.title.set_color('white')
            ax.spines['bottom'].set_color('white')
            ax.spines['top'].set_color('white')
            ax.spines['left'].set_color('white')
            ax.spines['right'].set_color('white')

        self.ax1.legend()
        self.ax2.legend()
        self.ax1.grid(True)
        self.ax2.grid(True)
        self.fig.tight_layout()

    def update_plot(self, time, Vc, I, V0=10, animate=True, interval=50, circuit_diagram=None): # pylint: disable=invalid-name,too-many-arguments,too-many-positional-arguments,too-many-locals,too-many-statements
        """Update the plot with voltage and current data, optionally animating.

        Args:
            time: Array of time points for the simulation.
            Vc: Array of capacitor voltage values.
            I: Array of current values.
            V0: Initial voltage or EMF of the source, defaults to 10.
            animate: If True, animate the plot, defaults to True.
            interval: Animation frame interval in milliseconds, defaults to 50.
            circuit_diagram: CircuitDiagram widget to update charge level, defaults to None.

        Raises:
            ValueError: If input arrays are empty, invalid, or contain non-numeric values.
            TypeError: If input arrays have incompatible types.
            IndexError: If array slicing fails due to mismatched lengths.
            RuntimeError: If matplotlib operations (e.g., animation or rendering) fail.
        """
        try:
            if not all(isinstance(arr, (list, np.ndarray)) and len(arr) > 0 for arr in [time, Vc, I]):  # pylint: disable=line-too-long
                raise ValueError("Входные данные пусты или некорректны")
            if not all(np.isfinite(arr).all() for arr in [time, Vc, I]):
                raise ValueError("Данные содержат нечисловые значения")

            logging.debug("Данные для графика: time_len=%s, Vc_len=%s, I_len=%s",
                          len(time), len(Vc), len(I))
            logging.debug("Пример данных: time=%s, Vc=%s, I=%s",
                          time[:5], Vc[:5], I[:5])

            self.time = np.array(time)
            self.Vc = np.array(Vc)
            self.I = np.array(I)
            self.V0 = V0

            if self.anim is not None:
                self.anim.event_source.stop()
                self.anim = None

            self.ax1.clear()
            self.ax2.clear()
            self.line1, = self.ax1.plot([], [], label='Напряжение (В)', color='#00bfff')
            self.line2, = self.ax2.plot([], [], label='Ток (А)', color='#ffa500')
            self.setup_axes()

            self.line1.set_data(self.time, self.Vc)
            self.line2.set_data(self.time, self.I)
            self.ax1.set_xlim(0, max(self.time) if max(self.time) > 0 else 1)
            self.ax2.set_xlim(0, max(self.time) if max(self.time) > 0 else 1)
            v_min, v_max = min(self.Vc), max(self.Vc)
            i_min, i_max = min(self.I), max(self.I)
            v_margin = (v_max - v_min) * 0.1 or 0.1
            i_margin = (i_max - i_min) * 0.1 or 0.1
            self.ax1.set_ylim(v_min - v_margin, v_max + v_margin)
            self.ax2.set_ylim(i_min - i_margin, i_max + i_margin)

            if animate:
                def init():
                    logging.debug("Инициализация анимации")
                    self.line1.set_data([], [])
                    self.line2.set_data([], [])

                    if circuit_diagram:
                        circuit_diagram.set_charge_level(0, self.V0)

                    return self.line1, self.line2

                def update(frame):
                    logging.debug("Обновление кадра %s", frame)
                    self.line1.set_data(self.time[:frame], self.Vc[:frame])
                    self.line2.set_data(self.time[:frame], self.I[:frame])

                    if circuit_diagram:
                        circuit_diagram.set_charge_level(self.Vc[frame-1] if frame > 0 else 0, self.V0) # pylint: disable=line-too-long

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

            self.canvas.draw()
            self.canvas.flush_events()
            logging.debug("График отрисован")
        except (ValueError, TypeError, IndexError, RuntimeError) as e:
            logging.error("Ошибка при обновлении графика: %s", str(e))
            self.ax1.clear()
            self.ax2.clear()
            self.setup_axes()
            self.canvas.draw()
