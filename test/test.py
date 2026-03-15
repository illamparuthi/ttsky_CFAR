import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, ClockCycles


@cocotb.test()
async def test_cfar_target_detected(dut):
    """Feed background noise then a large spike — detector must fire."""

    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())

    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0

    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 5)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 2)

    detected = False

    # Fill training window fully (32 cycles to be safe)
    for _ in range(32):
        dut.ui_in.value = 10
        await RisingEdge(dut.clk)

    # Inject a strong target spike
    dut.ui_in.value = 255
    await RisingEdge(dut.clk)

    # Allow pipeline to propagate (extra cycles for GL gate delays)
    for _ in range(100):
        await RisingEdge(dut.clk)
        if int(dut.uo_out.value) & 1:
            detected = True

    assert detected, "CFAR detector failed to detect the target spike"


@cocotb.test()
async def test_cfar_no_false_alarm(dut):
    """Uniform low noise — detector must NOT fire after window is fully primed."""

    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())

    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0

    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 5)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 2)

    # Prime the window fully first (32 cycles)
    for _ in range(32):
        dut.ui_in.value = 10
        await RisingEdge(dut.clk)

    # Now check — uniform noise must NOT trigger detection
    false_alarm = False
    for _ in range(32):
        dut.ui_in.value = 10
        await RisingEdge(dut.clk)
        if int(dut.uo_out.value) & 1:
            false_alarm = True

    assert not false_alarm, "CFAR produced a false alarm on uniform noise"


@cocotb.test()
async def test_buzzer_activates(dut):
    """Buzzer output (uo_out[1]) must go high when target is detected."""

    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())

    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0

    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 5)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 2)

    # Prime training window
    for _ in range(32):
        dut.ui_in.value = 8
        await RisingEdge(dut.clk)

    # Keep spike sustained — buzzer square wave needs cycles to toggle
    buzzer_seen = False
    for _ in range(200):
        dut.ui_in.value = 250
        await RisingEdge(dut.clk)
        if (int(dut.uo_out.value) >> 1) & 1:
            buzzer_seen = True

    assert buzzer_seen, "Buzzer output did not activate after target detection"
