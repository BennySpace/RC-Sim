"""Module for calculating RC circuit parameters with non-ideal source support."""

import logging
from typing import Optional
import numpy as np


class RCCalculator:  # pylint: disable=too-many-instance-attributes
    """Class to calculate RC circuit parameters including EMF and internal resistance."""
    # Constants for default values and calculations
    DEFAULT_CAPACITANCE: float = 1e-6  # Farads
    DEFAULT_RESISTANCE: float = 1000  # Ohms
    DEFAULT_EMF: float = 10  # Volts
    DEFAULT_INTERNAL_RESISTANCE: float = 0  # Ohms
    DEFAULT_TEMP_COEFF: float = 0.0001  # 1/°C
    DEFAULT_TEMPERATURE: float = 25  # °C
    DEFAULT_TIME_STEP: float = 0.00001  # Seconds
    TAU_MULTIPLIER: float = 5
    AC_FREQUENCY: float = 50  # Hz
    PI: float = 2 * np.pi
    ENERGY_COEFF: float = 0.5
    REFERENCE_TEMPERATURE: float = 25  # °C

    def __init__(self) -> None:
        """Initialize the RC calculator with default parameters."""
        self.C: float = self.DEFAULT_CAPACITANCE  # pylint: disable=invalid-name
        self.R: float = self.DEFAULT_RESISTANCE  # pylint: disable=invalid-name
        self.V0: float = self.DEFAULT_EMF  # pylint: disable=invalid-name
        self.R_int: float = self.DEFAULT_INTERNAL_RESISTANCE  # pylint: disable=invalid-name
        self.source_type: str = 'DC'
        self.alpha: float = self.DEFAULT_TEMP_COEFF
        self.temperature: float = self.DEFAULT_TEMPERATURE
        self.time: Optional[np.ndarray] = None
        self.Vc: Optional[np.ndarray] = None  # pylint: disable=invalid-name
        self.I: Optional[np.ndarray] = None  # pylint: disable=invalid-name
        self.energy: float = 0
        self.power_loss: float = 0
        self.tau: float = 0
        self.phase_shift: float = 0

        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[logging.StreamHandler()]
        )

    def set_parameters(  # pylint: disable=too-many-arguments,too-many-positional-arguments
            self,
            C: float,  # pylint: disable=invalid-name
            R: float,  # pylint: disable=invalid-name
            V0: float,  # pylint: disable=invalid-name
            source_type: str,
            alpha: float,
            temperature: float,
            R_int: float = DEFAULT_INTERNAL_RESISTANCE  # pylint: disable=invalid-name
    ) -> bool:
        """Set RC circuit parameters and validate them.

        Args:
            C: Capacitance in Farads.
            R: Resistance in Ohms.
            V0: EMF in Volts.
            source_type: Source type ('DC' or 'AC').
            alpha: Temperature coefficient in 1/°C.
            temperature: Temperature in °C.
            R_int: Internal resistance in Ohms (default: 0).

        Returns:
            True if parameters are valid, False otherwise.
        """
        if C <= 0 or R <= 0 or V0 <= 0 or R_int < 0:
            logging.error("Parameters must be positive (R_int can be 0)")
            return False

        self.C = C
        self.R = R
        self.V0 = V0
        self.R_int = R_int
        self.source_type = source_type
        self.alpha = alpha
        self.temperature = temperature
        logging.debug(  # pylint: disable=logging-fstring-interpolation
            f"Parameters set: C={C}, R={R}, V0={V0}, R_int={R_int}, "
            f"source_type={source_type}, alpha={alpha}, temperature={temperature}"
        )
        return True

    def calculate(self, time_step: float = DEFAULT_TIME_STEP, discharge: bool = False) -> bool:
        """Calculate RC circuit behavior over time.

        Args:
            time_step: Time step for simulation in seconds (default: 0.00001).
            discharge: If True, calculate discharge; if False, calculate charge (default: False).

        Returns:
            True if calculations succeed, False otherwise.
        """
        # pylint: disable=line-too-long,invalid-name
        try:
            R_temp = self.R * (1 + self.alpha * (
                        self.temperature - self.REFERENCE_TEMPERATURE)) + self.R_int
            self.tau = R_temp * self.C

            if self.tau <= 0 or not np.isfinite(self.tau):
                logging.error(f"Invalid time constant: tau={self.tau}")  # pylint: disable=logging-fstring-interpolation
                return False

            t_max = self.TAU_MULTIPLIER * self.tau
            num_points = int(t_max / time_step) + 1
            self.time = np.linspace(0, t_max, num_points)

            if self.source_type == 'DC':
                if discharge:
                    self.Vc = self.V0 * np.exp(-self.time / self.tau)  # pylint: disable=invalid-unary-operand-type
                    self.I = -(self.V0 / R_temp) * np.exp(
                        -self.time / self.tau)  # pylint: disable=invalid-unary-operand-type
                else:
                    self.Vc = self.V0 * (
                                1 - np.exp(-self.time / self.tau))  # pylint: disable=invalid-unary-operand-type
                    self.I = (self.V0 / R_temp) * np.exp(
                        -self.time / self.tau)  # pylint: disable=invalid-unary-operand-type
                self.phase_shift = 0
            else:
                omega = self.PI * self.AC_FREQUENCY
                Z = np.sqrt(R_temp ** 2 + (1 / (omega * self.C)) ** 2)  # pylint: disable=invalid-name
                self.Vc = (
                        self.V0 * np.sin(omega * self.time) /
                        np.sqrt(1 + (omega * R_temp * self.C) ** 2)
                )
                self.I = (
                        (self.V0 / Z) *
                        np.sin(omega * self.time - np.arctan(1 / (omega * R_temp * self.C)))
                )
                self.phase_shift = np.arctan(1 / (omega * R_temp * self.C))

            self.energy = self.ENERGY_COEFF * self.C * self.Vc[-1] ** 2
            self.power_loss = np.mean(self.I ** 2 * R_temp)

            if not all(np.isfinite(arr).all() for arr in [self.time, self.Vc, self.I]):
                logging.error("Results contain non-numeric values")
                return False

            logging.debug(  # pylint: disable=logging-fstring-interpolation
                f"Calculations completed: tau={self.tau:.6f}, "
                f"energy={self.energy:.6f}, power_loss={self.power_loss:.6f}"
            )
            logging.debug(  # pylint: disable=logging-fstring-interpolation
                f"Results: time_len={len(self.time)}, "
                f"time_first5={self.time[:5]}, Vc_first5={self.Vc[:5]}, I_first5={self.I[:5]}"
            )
            return True
        except ValueError as e:
            logging.error(f"Calculation error: {str(e)}")  # pylint: disable=logging-fstring-interpolation
            return False
