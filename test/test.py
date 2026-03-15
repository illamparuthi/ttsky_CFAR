import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, ClockCycles, Timer


def safe_bit(signal, bit):
    """Read one bit safely — returns 0 for X/Z (common in GL sim)."""
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
    await ClockCycles(dut.clk, 15)   # longer reset flush for GL X-state
    dut.rst_n.value  = 1
    await ClockCycles(dut.clk, 10)   # extra settle for GL gate delays


async def prime_window(dut, value, cycles):
    for _ in range(cycles):
        dut.ui_in.value = value
        await RisingEdge(dut.clk)


@cocotb.test()
async def test_cfar_target_detected(dut):
    """Prime window noise=10, send spike=200 for 6 cycles, then noise.
    GL sim has ~3-4 cycle gate delay — sample output over 30 cycles."""

    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())
    await reset_dut(dut)
    await prime_window(dut, value=10, cycles=32)

    # Send spike for 6 cycles then back to noise
    for _ in range(6):
        dut.ui_in.value = 200
        await RisingEdge(dut.clk)

    # Sample over 30 post-spike cycles (GL needs extra cycles for gate settling)
    # Simulation shows detect fires at noise cycles 2-5 in RTL;
    # GL may shift this by 3-4 cycles due to unit gate delays
    detected = False
    for _ in range(30):
        dut.ui_in.value = 10
        await RisingEdge(dut.clk)
        # Read after a small settle time within the clock period
        await Timer(5, units="ns")
        if safe_bit(dut.uo_out, 0) == 1:
            detected = True

    assert detected, "CFAR did not detect target spike (uo_out[0] never went high)"


@cocotb.test()
async def test_cfar_no_false_alarm(dut):
    """Uniform noise — detect must stay low."""

    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())
    await reset_dut(dut)
    await prime_window(dut, value=10, cycles=32)

    false_alarm = False
    for _ in range(32):
        dut.ui_in.value = 10
        await RisingEdge(dut.clk)
        await Timer(5, units="ns")
        if safe_bit(dut.uo_out, 0) == 1:
            false_alarm = True

    assert not false_alarm, "CFAR false alarm on uniform noise"


@cocotb.test()
async def test_buzzer_activates(dut):
    """Spike burst triggers detect for ~4 cycles → buzzer latches hold=2000.
    half_period=250 (strength=80) → first toggle at ~250 cycles after latch.
    Watch 3000 cycles to catch it even with GL gate-delay shift."""

    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())
    await reset_dut(dut)
    await prime_window(dut, value=8, cycles=32)

    # Spike burst — triggers detect for ~4 cycles
    for _ in range(6):
        dut.ui_in.value = 200
        await RisingEdge(dut.clk)

    # Back to noise — buzzer hold latch keeps tone going for 2000 cycles
    buzzer_seen = False
    for _ in range(3000):
        dut.ui_in.value = 8
        await RisingEdge(dut.clk)
        await Timer(5, units="ns")
        if safe_bit(dut.uo_out, 1) == 1:
            buzzer_seen = True
            break

    assert buzzer_seen, "Buzzer did not activate (uo_out[1] never went high)"
