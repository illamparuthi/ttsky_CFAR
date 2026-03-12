import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge


@cocotb.test()
async def test_project(dut):

    # Start clock
    clock = Clock(dut.clk, 10, unit="ns")
    cocotb.start_soon(clock.start())

    # Initialize signals
    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.rst_n.value = 0

    # Reset for a few cycles
    for _ in range(5):
        await RisingEdge(dut.clk)

    dut.rst_n.value = 1

    # Feed background noise
    noise = [10, 11, 9, 10, 12, 11, 10]

    for val in noise:
        dut.ui_in.value = val
        await RisingEdge(dut.clk)

    # Inject strong reflection (target)
    dut.ui_in.value = 80
    await RisingEdge(dut.clk)

    # Continue normal noise
    for val in [11, 10, 9, 10]:
        dut.ui_in.value = val
        await RisingEdge(dut.clk)

    # Allow pipeline to propagate (CFAR window delay)
    detected = False

    for _ in range(20):
        await RisingEdge(dut.clk)

        if int(dut.uo_out.value) != 0:
            detected = True

    # Check detection occurred
    assert detected, "CFAR detector failed to detect strong reflection"
