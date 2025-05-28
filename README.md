# RC-Sim: RC Circuit Simulator

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![PyQt6](https://img.shields.io/badge/PyQt6-6.0%2B-orange)

**RC-Sim** is an interactive application for simulating transient processes in an RC circuit (capacitor charging and discharging) with a graphical user interface. The program allows users to configure circuit parameters, visualize voltage and current in real-time with animation, and export results to CSV for further analysis.

## Features

- **Interactive Interface**: Configure circuit parameters (capacitance, resistance, voltage, source type, temperature).
- **Operating Modes**: Supports capacitor charging and discharging for both DC and AC sources.
- **Animation**: Smooth visualization of voltage and current with adjustable speed.
- **Circuit Diagram**: Dynamic display of the capacitor's charge level.
- **Data Export**: Save results to CSV with customizable precision and decimal separator (point or comma).
- **CSV Preview**: Preview data before exporting.
- **Graph Saving**: Export graphs as PNG images.
- **Logging**: Detailed debug messages for diagnostics.

## Requirements

- Python 3.8 or higher
- Libraries:
  - `PyQt6 >= 6.0`
  - `matplotlib >= 3.2`
  - `numpy >= 1.20`

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/username/rc-simulator.git
   cd rc-simulator
   ```

2. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the application:
   ```bash
   python main.py
   ```

## `requirements.txt` File

```plaintext
PyQt6>=6.0.1
matplotlib>=3.2.0
numpy>=1.20.0
```

## Usage

1. Launch the application with `python main.py`.
2. Configure circuit parameters:
   - **Capacitance (µF)**: E.g., `1` for 1 µF.
   - **Resistance (Ω)**: E.g., `1000`.
   - **Voltage (V)**: E.g., `10`.
   - **Source Type**: `DC` or `AC`.
   - **Mode**: `Charging` or `Discharging`.
   - **Temperature Coefficient (1/°C)**: E.g., `0.0001`.
   - **Temperature (°C)**: E.g., `25`.
   - **Export Precision**: Number of decimal places (1–12).
   - **Decimal Separator**: Point (.) or comma (,).
3. Adjust animation speed using the slider (10–200 ms).
4. Click **"Run Simulation"** to start the simulation.
5. Use the buttons:
   - **Pause/Resume**: Control the animation.
   - **Preview CSV**: View data before exporting.
   - **Export to CSV**: Save data (~1000 points).
   - **Save Graph**: Export the graph as PNG.
   - **Help**: View usage instructions.
   - **Exit**: Close the application.

## Project Structure

```plaintext
rc-simulator/
├── main.py                 # Application entry point
├── rc_calculator.py        # RC circuit calculation logic
├── plot_widget.py          # Widget for graphs with animation
├── circuit_diagram.py      # RC circuit diagram visualization
├── help_window.py          # Help window
├── requirements.txt        # Dependencies
└── README.md               # Documentation
```

## CSV Export Examples

**Charging Mode**, precision=6, separator=point:
```csv
Time (s);Voltage (V);Current (A)
0;0;0.01
0.00001;0.00995;0.009901
0.00002;0.0198;0.009802
...
0.005;9.932621;0.000067
```

**Discharging Mode**, precision=4, separator=comma:
```csv
Time (s);Voltage (V);Current (A)
0;10;-0,01
0,00001;9,9901;-0,0099
0,00002;9,9802;-0,0098
...
0,005;0,0674;-0,0001
```

---

**RC-Sim** is the perfect tool for studying RC circuits and analyzing transient processes. Try it now! 🚀
