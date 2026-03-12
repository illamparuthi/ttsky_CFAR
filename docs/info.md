## How it works

This project implements a **CA-CFAR (Cell Averaging Constant False Alarm Rate)** detector for radar or Ground Penetrating Radar (GPR) signal processing.

The CFAR algorithm detects strong reflections in radar signals by comparing a **Cell Under Test (CUT)** with a threshold calculated from surrounding noise samples.

The design maintains a sliding window of 11 samples:

Training Cells | Guard | CUT | Guard | Training Cells

Training cells estimate the background noise level, while guard cells prevent the target signal from influencing the noise estimation.

The detector computes the threshold as:

threshold = 2 × average(training cells)

If the signal value of the CUT is greater than the threshold, the circuit outputs:

detect = 1

Otherwise:

detect = 0

### Architecture

Radar Sample Input  
↓  
Sliding Window Registers  
↓  
Training Cell Adder Tree  
↓  
Average Calculator  
↓  
Threshold Generator  
↓  
Comparator  
↓  
Detection Output


## How to test

1. Provide radar sample data through the input pins `ui_in[7:0]`.
2. Apply a clock signal to `clk`.
3. Reset the design by setting `rst_n = 0`.
4. Release reset by setting `rst_n = 1`.
5. Feed a sequence of radar samples to the input.

The detector continuously shifts incoming samples through the sliding window and calculates the noise level.

When a strong reflection enters the **Cell Under Test (CUT)** and exceeds the calculated threshold, the detection output is asserted.

Output:

- `uo_out[0] = 1` → target detected  
- `uo_out[0] = 0` → no target detected

Example test input sequence:

10, 11, 9, 10, 12, 11, 10, 80, 11, 10

When the value **80** reaches the CUT position, the detector should assert `uo_out[0] = 1`.


## External hardware

No external hardware is required.

The project operates entirely as a digital logic block and can be tested through simulation or when integrated into a TinyTapeout chip.
