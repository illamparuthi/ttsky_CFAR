import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge

@cocotb.test()
async def test_project(dut):

```
# Start clock (10 ns period)
clock = Clock(dut.clk, 10, unit="ns")
cocotb.start_soon(clock.start())

# Enable design
dut.ena.value = 1
dut.ui_in.value = 0
dut.uio_in.value = 0

# Apply reset
dut.rst_n.value = 0
for _ in range(5):
    await RisingEdge(dut.clk)

dut.rst_n.value = 1

# Radar input samples (one strong target)
samples = [10, 11, 9, 10, 12, 11, 10, 255, 11, 10]

detected = False

# Feed samples into DUT
for s in samples:
    dut.ui_in.value = s
    await RisingEdge(dut.clk)

    # Check detection output
    if int(dut.uo_out.value) & 1:
        detected = True

# Extra cycles for pipeline delay (important for GL sim)
for _ in range(80):
    await RisingEdge(dut.clk)
    if int(dut.uo_out.value) & 1:
        detected = True

assert detected, "CFAR detector failed to detect target"
```
