import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, ClockCycles


def safe_bit(signal, bit):
    """Read one bit safely — returns 0 for X/Z (GL sim startup)."""
    try:
        s = str(signal.value[bit])
        return 1 if s == '1' else 0
    except Exception:
        return 0


async def reset_dut(dut):
    dut.ena.value    = 1
    dut.ui_in.value  = 0
    dut.uio_in.value = 0
    dut.rst_n.value  = 0
    await ClockCycles(dut.clk, 15)
    dut.rst_n.value  = 1
    await ClockCycles(dut.clk, 10)


async def prime_window(dut, value, cycles):
    for _ in range(cycles):
        dut.ui_in.value = value
        await RisingEdge(dut.clk)


@cocotb.test()
async def test_cfar_target_detected(dut):
    """Prime noise=10, spike=200 for 6 cycles, then noise.
    detect fires when spike sits at CUT (w5) while training=noise."""

    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())
    await reset_dut(dut)
    await prime_window(dut, value=10, cycles=32)

    for _ in range(6):
        dut.ui_in.value = 200
        await RisingEdge(dut.clk)

    detected = False
    for _ in range(30):
        dut.ui_in.value = 10
        await RisingEdge(dut.clk)
        if safe_bit(dut.uo_out, 0) == 1:
            detected = True

    assert detected, "CFAR did not detect target spike (uo_out[0] never went high)"


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
    """Spike burst → detect fires ~4 cycles → buzzer latches hold=2000 cycles.
    strength=80 at detection time → half_period=250 → toggle at ~250 cycles."""

    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())
    await reset_dut(dut)
    await prime_window(dut, value=8, cycles=32)

    for _ in range(6):
        dut.ui_in.value = 200
        await RisingEdge(dut.clk)

    buzzer_seen = False
    for _ in range(3000):
        dut.ui_in.value = 8
        await RisingEdge(dut.clk)
        if safe_bit(dut.uo_out, 1) == 1:
            buzzer_seen = True
            break

    assert buzzer_seen, "Buzzer did not activate (uo_out[1] never went high)"
