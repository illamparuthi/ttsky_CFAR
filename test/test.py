import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge


@cocotb.test()
async def test_project(dut):

    # start clock
    clock = Clock(dut.clk, 10, unit="ns")
    cocotb.start_soon(clock.start())

    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0

    # reset
    dut.rst_n.value = 0
    for _ in range(5):
        await RisingEdge(dut.clk)

    dut.rst_n.value = 1

    # radar samples
    samples = [10,11,9,10,12,11,10,200,11,10]

    detected = False

    for s in samples:
        dut.ui_in.value = s
        await RisingEdge(dut.clk)

        # check detection bit each cycle
        if dut.uo_out.value[0] == 1:
            detected = True

    # wait extra cycles for pipeline
    for _ in range(10):
        await RisingEdge(dut.clk)
        if dut.uo_out.value[0] == 1:
            detected = True

    assert detected, "CFAR detector failed to detect target"
