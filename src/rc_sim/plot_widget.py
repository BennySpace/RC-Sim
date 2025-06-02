from PyQt6.QtWidgets import QWidget, QVBoxLayout
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.animation import FuncAnimation
import numpy as np
import logging


class PlotWidget(QWidget):
    def __init__(self, parent=None):
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
        self.Vc = []
        self.I = []
        self.V0 = 10


    def setup_axes(self):
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


    def update_plot(self, time, Vc, I, V0=10, animate=True, interval=50, circuit_diagram=None):
        try:
            if not all(isinstance(arr, (list, np.ndarray)) and len(arr) > 0 for arr in [time, Vc, I]):
                raise ValueError("Входные данные пусты или некорректны")
            if not all(np.isfinite(arr).all() for arr in [time, Vc, I]):
                raise ValueError("Данные содержат нечисловые значения")

            logging.debug(f"Данные для графика: time_len={len(time)}, Vc_len={len(Vc)}, I_len={len(I)}")
            logging.debug(f"Пример данных: time={time[:5]}, Vc={Vc[:5]}, I={I[:5]}")

            self.time = np.array(time)
            self.Vc = np.array(Vc)
            self.I = np.array(I)
            self.V0 = V0

            if self.anim is not None:
                self.anim.event_source.stop()
                self.anim = None

            self.ax1.clear()
            self.ax2.clear()
            self.line1, = self.ax1.plot([], [], label='Напряжение (В)', color='blue')
            self.line2, = self.ax2.plot([], [], label='Ток (А)', color='red')
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
                    logging.debug(f"Обновление кадра {frame}")
                    self.line1.set_data(self.time[:frame], self.Vc[:frame])
                    self.line2.set_data(self.time[:frame], self.I[:frame])

                    if circuit_diagram:
                        circuit_diagram.set_charge_level(self.Vc[frame-1] if frame > 0 else 0, self.V0)

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
        except Exception as e:
            logging.error(f"Ошибка при обновлении графика: {str(e)}")
            self.ax1.clear()
            self.ax2.clear()
            self.setup_axes()
            self.canvas.draw()
