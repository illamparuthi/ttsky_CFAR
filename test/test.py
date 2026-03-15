import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, ClockCycles


def safe_bit(signal, bit):
    """Read one bit safely — returns 0 for X/Z (common in GL sim)."""
    try:
        s = str(signal.value[bit])
        return 1 if s == '1' else 0
    except Exception:
        return 0


@cocotb.test()
async def test_cfar_target_detected(dut):
    """Fill window with low noise, then spike — detect bit must go high."""

    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())

    dut.ena.value   = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.rst_n.value  = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 5)

    # Prime all 11 window cells with low noise
    for _ in range(32):
        dut.ui_in.value = 10
        await RisingEdge(dut.clk)

    # Strong target spike — threshold = 2*10 = 20, spike = 200 >> 20
    dut.ui_in.value = 200
    await RisingEdge(dut.clk)

    detected = False
    for _ in range(20):
        await RisingEdge(dut.clk)
        if safe_bit(dut.uo_out, 0) == 1:
            detected = True
            break

    assert detected, f"CFAR did not detect target spike (uo_out={dut.uo_out.value})"


@cocotb.test()
async def test_cfar_no_false_alarm(dut):
    """Uniform noise — detect must stay low once window is fully primed."""

    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())

    dut.ena.value    = 1
    dut.ui_in.value  = 0
    dut.uio_in.value = 0
    dut.rst_n.value  = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 5)

    # Prime window
    for _ in range(32):
        dut.ui_in.value = 10
        await RisingEdge(dut.clk)

    # Check: uniform input must NOT trigger detection
    false_alarm = False
    for _ in range(32):
        dut.ui_in.value = 10
        await RisingEdge(dut.clk)
        if safe_bit(dut.uo_out, 0) == 1:
            false_alarm = True

    assert not false_alarm, "CFAR false alarm on uniform noise"


@cocotb.test()
async def test_buzzer_activates(dut):
    """Buzzer bit (uo_out[1]) must toggle when detect is sustained.
    With fixed buzzer.v limit=500 cycles, it toggles within 600 cycles.
    """

    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())

    dut.ena.value    = 1
    dut.ui_in.value  = 0
    dut.uio_in.value = 0
    dut.rst_n.value  = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 5)

    # Prime window with low noise
    for _ in range(32):
        dut.ui_in.value = 8
        await RisingEdge(dut.clk)

    # Sustain large spike — keeps detect=1 so buzzer counter keeps running
    # With strength=avg=8, limit=1667 → buzzer toggles after 1667 cycles
    buzzer_seen = False
    for _ in range(5000):
        dut.ui_in.value = 200
        await RisingEdge(dut.clk)
        if safe_bit(dut.uo_out, 1) == 1:
            buzzer_seen = True
            break

    assert buzzer_seen, "Buzzer did not activate (uo_out[1] never went high)"
