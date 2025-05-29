import numpy as np
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s', handlers=[logging.StreamHandler()])

class RCCalculator:
    def __init__(self):
        self.C = 1e-6  # Ёмкость (Ф)
        self.R = 1000  # Сопротивление (Ом)
        self.V0 = 10   # Напряжение (В)
        self.source_type = 'DC'
        self.alpha = 0.0001  # Температурный коэффициент
        self.temperature = 25  # Температура (°C)
        self.time = None
        self.Vc = None
        self.I = None
        self.energy = 0
        self.power_loss = 0
        self.tau = 0
        self.phase_shift = 0

    def set_parameters(self, C, R, V0, source_type, alpha, temperature):
        if C <= 0 or R <= 0 or V0 <= 0:
            logging.error("Параметры должны быть положительными")
            return False
        self.C = C
        self.R = R
        self.V0 = V0
        self.source_type = source_type
        self.alpha = alpha
        self.temperature = temperature
        logging.debug(f"Параметры установлены: C={C}, R={R}, V0={V0}, source_type={source_type}, alpha={alpha}, temperature={temperature}")
        return True

    def calculate(self, time_step=0.00001, discharge=False):
        try:
            R_temp = self.R * (1 + self.alpha * (self.temperature - 25))
            self.tau = R_temp * self.C
            if self.tau <= 0 or not np.isfinite(self.tau):
                logging.error(f"Некорректная постоянная времени: tau={self.tau}")
                return False

            t_max = 5 * self.tau
            num_points = int(t_max / time_step) + 1
            self.time = np.linspace(0, t_max, num_points)

            if self.source_type == 'DC':
                if discharge:
                    self.Vc = self.V0 * np.exp(-self.time / self.tau)
                    self.I = -(self.V0 / R_temp) * np.exp(-self.time / self.tau)
                else:
                    self.Vc = self.V0 * (1 - np.exp(-self.time / self.tau))
                    self.I = (self.V0 / R_temp) * np.exp(-self.time / self.tau)
                self.phase_shift = 0
            else:
                freq = 50
                omega = 2 * np.pi * freq
                Z = np.sqrt(R_temp**2 + (1 / (omega * self.C))**2)
                self.Vc = self.V0 * np.sin(omega * self.time) / np.sqrt(1 + (omega * R_temp * self.C)**2)
                self.I = (self.V0 / Z) * np.sin(omega * self.time - np.arctan(1 / (omega * R_temp * self.C)))
                self.phase_shift = np.arctan(1 / (omega * R_temp * self.C))

            self.energy = 0.5 * self.C * self.Vc[-1]**2
            self.power_loss = np.mean(self.I**2 * R_temp)

            if not all(np.isfinite(arr).all() for arr in [self.time, self.Vc, self.I]):
                logging.error("Результаты содержат нечисловые значения")
                return False

            logging.debug(f"Расчёты выполнены: tau={self.tau:.6f}, energy={self.energy:.6f}, power_loss={self.power_loss:.6f}")
            logging.debug(f"Results: time_len={len(self.time)}, time_first5={self.time[:5]}, Vc_first5={self.Vc[:5]}, I_first5={self.I[:5]}")
            return True
        except Exception as e:
            logging.error(f"Ошибка в расчётах: {str(e)}")
            return False