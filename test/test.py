import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, ClockCycles


@cocotb.test()
async def test_cfar_target_detected(dut):
    """Feed background noise then a large spike — detector must fire."""

    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())

    # Initialize inputs
    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0

    # Reset
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 5)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 2)

    detected = False

    # Fill training window with low background noise first
    for _ in range(16):
        dut.ui_in.value = 10
        await RisingEdge(dut.clk)
        if int(dut.uo_out.value) & 1:
            detected = True

    # Inject a strong target spike (well above 2x average noise of 10)
    dut.ui_in.value = 255
    await RisingEdge(dut.clk)

    # Allow pipeline to propagate
    for _ in range(80):
        await RisingEdge(dut.clk)
        if int(dut.uo_out.value) & 1:
            detected = True

    assert detected, "CFAR detector failed to detect the target spike"


@cocotb.test()
async def test_cfar_no_false_alarm(dut):
    """Uniform low noise — detector must NOT fire."""

    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())

    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0

    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 5)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 2)

    false_alarm = False

    # Feed uniform noise — no target should be detected
    for _ in range(40):
        dut.ui_in.value = 10
        await RisingEdge(dut.clk)
        if int(dut.uo_out.value) & 1:
            false_alarm = True

    assert not false_alarm, "CFAR produced a false alarm on uniform noise"


@cocotb.test()
async def test_buzzer_activates(dut):
    """Buzzer output (bit 1) must go high when target is detected."""

    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())

    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0

    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 5)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 2)

    buzzer_seen = False

    # Prime with low noise
    for _ in range(16):
        dut.ui_in.value = 8
        await RisingEdge(dut.clk)

    # Large spike
    dut.ui_in.value = 250
    await RisingEdge(dut.clk)

    # Let buzzer propagate
    for _ in range(80):
        await RisingEdge(dut.clk)
        if (int(dut.uo_out.value) >> 1) & 1:
            buzzer_seen = True

    assert buzzer_seen, "Buzzer output did not activate after target detection"
