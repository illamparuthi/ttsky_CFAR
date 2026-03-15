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


async def prime_window(dut, value=8, cycles=32):
    """Fill the CFAR training window with a uniform noise value."""
    for _ in range(cycles):
        dut.ui_in.value = value
        await RisingEdge(dut.clk)


async def reset_dut(dut):
    """Standard reset sequence."""
    dut.ena.value    = 1
    dut.ui_in.value  = 0
    dut.uio_in.value = 0
    dut.rst_n.value  = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value  = 1
    await ClockCycles(dut.clk, 5)


@cocotb.test()
async def test_cfar_target_detected(dut):
    """Prime window with noise=10, send spike=200 for 6 cycles, then noise.
    Spike sits at CUT (w5) after 5 shift cycles → detect must fire."""

    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())
    await reset_dut(dut)
    await prime_window(dut, value=10, cycles=32)

    # Send spike for 6 cycles then back to noise
    # (spike enters w0 at cycle 0, reaches w5/CUT at cycle 5-6)
    for _ in range(6):
        dut.ui_in.value = 200
        await RisingEdge(dut.clk)

    detected = False
    for _ in range(20):
        dut.ui_in.value = 10
        await RisingEdge(dut.clk)
        if safe_bit(dut.uo_out, 0) == 1:
            detected = True
            break

    assert detected, "CFAR did not detect spike (uo_out[0] never went high)"


@cocotb.test()
async def test_cfar_no_false_alarm(dut):
    """Uniform noise throughout — detect must stay low."""

    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())
    await reset_dut(dut)
    await prime_window(dut, value=10, cycles=32)

    false_alarm = False
    for _ in range(32):
        dut.ui_in.value = 10
        await RisingEdge(dut.clk)
        if safe_bit(dut.uo_out, 0) == 1:
            false_alarm = True

    assert not false_alarm, "CFAR false alarm on uniform noise"


@cocotb.test()
async def test_buzzer_activates(dut):
    """Send spike so CFAR detect fires, then buzzer latches and plays tone.
    Buzzer holds for HOLD_CYCLES=2000, toggling every half_period cycles.
    With strength~8 (low noise avg), half_period=1000 → first toggle at ~1000.
    We wait 3000 cycles total — enough for multiple toggles."""

    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())
    await reset_dut(dut)
    await prime_window(dut, value=8, cycles=32)

    # Send spike burst — triggers detect for ~4 cycles
    # buzzer latches and holds tone for 2000 cycles
    for _ in range(6):
        dut.ui_in.value = 200
        await RisingEdge(dut.clk)

    # Back to noise — buzzer should still be playing due to hold latch
    buzzer_seen = False
    for _ in range(3000):
        dut.ui_in.value = 8
        await RisingEdge(dut.clk)
        if safe_bit(dut.uo_out, 1) == 1:
            buzzer_seen = True
            break

    assert buzzer_seen, "Buzzer did not activate (uo_out[1] never went high)"
