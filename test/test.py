import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge


@cocotb.test()
async def test_project(dut):

    # Start clock
    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())

    # Initial values
    dut.ena.value = 1
    dut.rst_n.value = 0
    dut.ui_in.value = 0
    dut.uio_in.value = 0

    # Hold reset
    for _ in range(5):
        await RisingEdge(dut.clk)

    # Release reset
    dut.rst_n.value = 1

    # Radar samples
    samples = [10, 11, 12, 10, 11, 10, 9, 10, 80, 11, 10]

    for s in samples:
        dut.ui_in.value = s
        await RisingEdge(dut.clk)

    detected = False

    # Wait for pipeline to propagate
    for _ in range(20):
        await RisingEdge(dut.clk)

        # Check only detection bit (LSB)
        detect_bit = dut.uo_out.value[0]

        if detect_bit == 1:
            detected = True

    assert detected, "CFAR detector failed to detect target"
