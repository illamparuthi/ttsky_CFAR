# Testbench for CFAR Tiny Tapeout Project

This directory contains the simulation testbench for the **CFAR Radar Detector with Audio Alert** Tiny Tapeout project.

The testbench uses **cocotb** to drive the DUT (Device Under Test) and verify the outputs.

Documentation:  
https://tinytapeout.com/hdl/testing/

---

## Setting up

1. Edit the **Makefile** and ensure the Verilog source files are listed correctly.

Example:

```
PROJECT_SOURCES = project.v cfar.v buzzer.v
```

2. In **tb.v**, replace the example module with your wrapper module:

```
tt_um_ttsky_cfar user_project
```

---

## Running RTL simulation

Run the following command:

```
make -B
```

This compiles the Verilog design and runs the cocotb testbench.

---

## Gate-level simulation

To run gate-level simulation:

1. Harden your design using the Tiny Tapeout flow.
2. Copy the generated gate-level netlist from:

```
../runs/wokwi/results/final/verilog/gl/tt_um_ttsky_cfar.v
```

to:

```
gate_level_netlist.v
```

3. Run:

```
make -B GATES=yes
```

---

## Saving waveform files

By default the simulation saves waveform files in **FST format**.

To save waveforms in **VCD format**, modify `tb.v`:

```
$dumpfile("tb.vcd");
```

Then run:

```
make -B FST=
```

This will generate `tb.vcd`.

---

## Viewing waveforms

Using GTKWave:

```
gtkwave tb.fst
```

Using Surfer:

```
surfer tb.fst
```

---

## Test behavior

The testbench feeds radar samples into the CFAR detector.

Example input sequence:

```
10, 11, 9, 10, 12, 11, 10, 80, 11, 10
```

When the value **80** reaches the **Cell Under Test (CUT)** position, the detector should assert:

```
uo_out[0] = 1
```

indicating a detected radar target.

At the same time:

```
uo_out[1]
```

will generate a **buzzer signal** indicating detection.

---

## Project structure

```
src/
 ├── project.v        # TinyTapeout wrapper module
 ├── cfar.v           # CFAR detector logic
 └── buzzer.v         # Buzzer / audio alert generator

test/
 ├── tb.v             # Verilog testbench wrapper
 ├── tb.py            # cocotb test script
 └── Makefile         # simulation configuration
```
