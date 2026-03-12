
  ![](../../workflows/gds/badge.svg) ![](../../workflows/docs/badge.svg) ![](../../workflows/test/badge.svg) ![](../../workflows/fpga/badge.svg)

# CFAR Radar Detector – TinyTapeout Project

## Project Overview

This project implements a **CA-CFAR (Cell Averaging Constant False Alarm Rate) detector** in Verilog for radar or Ground Penetrating Radar (GPR) signal processing.

CFAR is a widely used radar detection algorithm that determines whether a target exists by comparing a **Cell Under Test (CUT)** with a **threshold calculated from surrounding noise samples**.

If the signal strength of the CUT exceeds the calculated threshold, a detection signal is generated.

---

## CFAR Detection Concept

The algorithm analyzes a sliding window of samples:

```
Training Cells | Guard | CUT | Guard | Training Cells
```

- **Training cells** estimate the background noise.
- **Guard cells** prevent the target signal from affecting the noise calculation.

Detection rule:

```
CUT > Threshold → Target detected
```

---

## Architecture

```
Radar Sample
     ↓
Sliding Window Register
     ↓
Noise Estimation (Adder Tree)
     ↓
Average Calculation
     ↓
Threshold Generator
     ↓
Comparator
     ↓
Detection Output
```

---

## Project Structure

```
src/
 ├── project.v          # TinyTapeout wrapper module
 └── cfar_detector.v    # CFAR detection logic

test/
 └── tb.v               # simulation testbench

docs/
 └── info.md            # project documentation
```

---

## Inputs and Outputs

| Signal | Description |
|------|-------------|
| `ui_in[7:0]` | Radar input samples |
| `uo_out[0]` | Detection output |
| `clk` | System clock |
| `rst_n` | Active-low reset |

---

## Detection Logic

The detector calculates the average noise level from surrounding training cells and generates a threshold.

```
threshold = 2 × average_noise
```

If:

```
CUT > threshold
```

Then:

```
detect = 1
```

---

## Simulation

You can simulate the design using **Icarus Verilog**.

Compile:

```
iverilog -o sim src/*.v test/tb.v
```

Run:

```
vvp sim
```

View waveforms:

```
gtkwave tb.fst
```

---

## What is Tiny Tapeout?

Tiny Tapeout is an educational project that allows designers to fabricate digital circuits on real silicon using open-source tools.

Learn more:  
https://tinytapeout.com

---

## Author

Illamparuthi

---

## License

Licensed under **Apache-2.0 License**.
