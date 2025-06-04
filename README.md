# RC-Simulator: Interactive RC Circuit Simulator

![Python](https://img.shields.io/badge/Python-3.8%2B-yellow)
![PyQt6](https://img.shields.io/badge/PyQt6-6.0%2B-orange)
![matplotlib](https://img.shields.io/badge/matplotlib-3.2.0%2B-blue)
![numpy](https://img.shields.io/badge/numpy-1.20.0%2B-darkblue)
![License](https://img.shields.io/badge/license-MIT-green)

**RC-Simulator** is a Python-based application designed to simulate and visualize the behavior of an RC (resistor-capacitor) circuit with a non-ideal power source. It provides an interactive graphical user interface (GUI) to configure circuit parameters, visualize voltage and current dynamics with real-time animations, and export results for further analysis. The simulator supports both DC and AC sources, as well as charging and discharging modes, making it an ideal tool for students, educators, and engineers studying transient processes in RC circuits.

Developed by **Daniil Vlasov** and **Alisa Yusupova** (Group P3213) under the supervision of **Nikolay Khvastunov**, Associate Professor and Candidate of Physical and Mathematical Sciences.

## Features

![image](https://github.com/user-attachments/assets/0c37c88f-3944-4e43-8312-602ec961785d)
![image](https://github.com/user-attachments/assets/6c0d78a8-9f85-4f50-9b22-b77307866d8a)

- **Interactive GUI**: Configure circuit parameters such as capacitance (µF), resistance (Ω), EMF (V), internal resistance (Ω), temperature (°C), and temperature coefficient (1/°C).
- **DC and AC Support**: Simulate circuits with constant (DC) or alternating (AC, 50 Hz) sources.
- **Charging and Discharging Modes**: Analyze both charging and discharging processes of the capacitor.
- **Real-Time Visualization**: Animated plots of voltage across the capacitor ($V_C$) and current ($I$) with adjustable animation speed (10–200 ms).
- **Circuit Diagram**: Dynamic visualization of the RC circuit with animated current flow and capacitor charge level indicators.
- **Data Export**: Save simulation data to CSV files with customizable precision (1–12 decimal places) and decimal separator (point or comma).
- **CSV Preview**: Preview exported data before saving.
- **Graph Export**: Save voltage and current plots as high-resolution PNG images (300 DPI).
- **Help Window**: Access detailed documentation with physical principles and equations rendered in LaTeX.
- **Logging**: Comprehensive debug logging for diagnostics and troubleshooting.

## Requirements

- **Python**: 3.8 or higher
- **Libraries**:
  - `PyQt6 >= 6.7.0`
  - `matplotlib >= 3.9.2`
  - `numpy >= 2.1.0`

## Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/username/rc-simulator.git
   cd rc-simulator
   ```

2. **Create a Virtual Environment** (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Application**:
   ```bash
   python main.py
   ```

### `requirements.txt`
```plaintext
PyQt6>=6.0.1
matplotlib>=3.2.0
numpy>=1.20.0
```

## Usage

1. Launch the application with:
   ```bash
   python main.py
   ```

2. Configure circuit parameters in the GUI:
   - **Capacitance (µF)**: E.g., `1` for 1 µF.
   - **Resistance (Ω)**: E.g., `1000`.
   - **EMF (V)**: E.g., `10`.
   - **Internal Resistance (Ω)**: E.g., `0`.
   - **Source Type**: Select `DC` or `AC`.
   - **Mode**: Choose `Charging` or `Discharging`.
   - **Temperature Coefficient (1/°C)**: E.g., `0.0001`.
   - **Temperature (°C)**: E.g., `25`.
   - **Export Precision**: Decimal places (1–12).
   - **Decimal Separator**: Point (.) or comma (,).

3. Adjust the animation speed using the slider (10–200 ms).

4. Click **Run Simulation** to start the simulation and view animated plots and circuit diagram.

5. Use the control buttons:
   - **Pause/Resume**: Toggle animation.
   - **Preview CSV**: View data before exporting.
   - **Export to CSV**: Save up to 1000 data points.
   - **Save Graph**: Export plots as PNG.
   - **Help**: View physical equations and usage guide.
   - **Exit**: Close the application.

## CSV Export Examples

**Charging Mode** (Precision=6, Separator=Point):
```csv
Time (s);Voltage (V);Current (A)
0;0;0.01
0.00001;0.00995;0.009901
0.00002;0.0198;0.009802
...
0.005;9.932621;0.000067
```

**Discharging Mode** (Precision=4, Separator=Comma):
```csv
Time (s);Voltage (V);Current (A)
0;10;-0,01
0,00001;9,9901;-0,0099
0,00002;9,9802;-0,0098
...
0,005;0,0674;-0,0001
```

## Project Structure

- `main.py`: Entry point for the application.
- `rc_simulator.py`: Main GUI window, integrating input, simulation, and export functionality.
- `rc_calculator.py`: Core calculations for RC circuit parameters.
- `plot_widget.py`: Handles plotting and animation of voltage and current.
- `circuit_diagram.py`: Renders the animated RC circuit diagram.
- `help_window.py`: Displays help documentation with LaTeX-rendered equations.

## Limitations

- AC source frequency is fixed at 50 Hz.
- CSV export is limited to 1000 data points.
- Export precision is restricted to 1–12 decimal places.
- AC source is assumed to be an ideal sinusoidal signal.
- Temperature effects are applied only to resistance.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Developed as an educational project by **Daniil Vlasov** and **Alisa Yusupova** (Group P3213).
- Supervised by **Nikolay Khvastunov**, Associate Professor and Candidate of Physical and Mathematical Sciences.
- Built with open-source libraries: PyQt6, NumPy, and Matplotlib.

---

**RC-Simulator** is a powerful tool for exploring RC circuit dynamics. Try it out and dive into the world of electronics! 🚀
