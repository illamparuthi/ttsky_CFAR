![](../../workflows/gds/badge.svg) ![](../../workflows/docs/badge.svg) ![](../../workflows/test/badge.svg) ![](../../workflows/fpga/badge.svg)

# CFAR Radar Detector with Audio Alert – TinyTapeout Project

## Project Overview

This project implements a **CA-CFAR (Cell Averaging Constant False Alarm Rate) radar detector** with an **audio alert output** using Verilog.

The system detects radar targets by comparing a **Cell Under Test (CUT)** with a **dynamic threshold derived from surrounding noise samples**.  
When a target is detected, a **buzzer signal is generated** to provide an audio indication.

This architecture can be used in:

- Ground Penetrating Radar (GPR)
- Automotive radar
- Object detection systems
- Embedded sensing devices

---

## CFAR Detection Concept

The CFAR algorithm processes a sliding window of radar samples:

```
Training Cells | Guard | CUT | Guard | Training Cells
```

- **Training cells** estimate the background noise level.
- **Guard cells** prevent the target signal from affecting the noise estimate.
- **CUT (Cell Under Test)** is the sample being evaluated.

Detection rule:

```
CUT > Threshold → Target detected
```

The threshold is calculated dynamically:

```
threshold = 2 × average_noise
```

---

## System Architecture

```
Radar Sample Input
        ↓
Sliding Window Registers
        ↓
Noise Estimation (Adder Tree)
        ↓
Average Calculation
        ↓
Threshold Generator
        ↓
Comparator
        ↓
Detection Signal
        ↓
Buzzer Controller
        ↓
Audio Alert Output
```

---

## Project Structure

```
src/
 ├── project.v          # TinyTapeout wrapper module
 ├── cfar.v             # CFAR detection logic
 └── buzzer.v           # Audio alert generator

test/
 ├── tb.v               # Verilog testbench
 └── tb.py              # Cocotb simulation test

docs/
 └── info.md            # Project documentation
```

---

## Inputs and Outputs

| Signal | Description |
|------|-------------|
| `ui_in[7:0]` | Radar input samples |
| `uo_out[0]` | CFAR detection output |
| `uo_out[1]` | Buzzer output signal |
| `clk` | System clock |
| `rst_n` | Active-low reset |

---

## Detection Logic

The detector calculates the average noise level from surrounding training cells and generates a dynamic threshold.

```
threshold = 2 × average_noise
```

Detection condition:

```
if (CUT > threshold)
    detect = 1
else
    detect = 0
```

When detection occurs, the buzzer module generates a square-wave tone.

---

## Simulation

The design can be simulated using **Icarus Verilog**.

Compile the design:

```
iverilog -o sim src/*.v test/tb.v
```

Run the simulation:

```
vvp sim
```

View waveforms:

```
gtkwave tb.fst
```

---

## What is Tiny Tapeout?

Tiny Tapeout is an educational initiative that allows designers to fabricate digital circuits on real silicon using open-source tools.

Learn more:

https://tinytapeout.com

---

## Author

Illamparuthi

---

## License

Licensed under the **Apache-2.0 License**.
