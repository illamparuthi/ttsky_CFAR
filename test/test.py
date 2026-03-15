import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, ClockCycles
from cocotb.types import LogicArray


def safe_read_bit(signal, bit):
    """Read a single bit safely — returns 0 if signal contains X/Z."""
    try:
        val = signal.value
        # LogicArray: check individual bit
        b = str(val[bit]) if hasattr(val, '__getitem__') else str(val)
        if b in ('0', '1'):
            return int(b)
        return 0
    except Exception:
        return 0


@cocotb.test()
async def test_cfar_target_detected(dut):
    """Feed background noise then a large spike — detector must fire."""

    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())

    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0

    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 5)

    detected = False

    # Fill training window fully with low noise
    for _ in range(32):
        dut.ui_in.value = 10
        await RisingEdge(dut.clk)

    # Inject a strong target spike
    dut.ui_in.value = 255
    await RisingEdge(dut.clk)

    # Allow pipeline to propagate
    for _ in range(100):
        await RisingEdge(dut.clk)
        if safe_read_bit(dut.uo_out, 0) == 1:
            detected = True
            break

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
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 5)

    # Prime the window fully first
    for _ in range(32):
        dut.ui_in.value = 10
        await RisingEdge(dut.clk)

    # Now check — uniform noise must NOT trigger detection
    false_alarm = False
    for _ in range(32):
        dut.ui_in.value = 10
        await RisingEdge(dut.clk)
        if safe_read_bit(dut.uo_out, 0) == 1:
            false_alarm = True

    assert not false_alarm, "CFAR produced a false alarm on uniform noise"


@cocotb.test()
async def test_buzzer_activates(dut):
    """Buzzer output (uo_out[1]) must go high when target is detected.
    The buzzer is a frequency divider — needs many clock cycles to toggle.
    At 10 MHz, even a 1 kHz buzzer needs 10000 cycles per period.
    We wait up to 50000 cycles to catch any toggle.
    """

    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())

    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0

    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 5)

    # Prime training window
    for _ in range(32):
        dut.ui_in.value = 8
        await RisingEdge(dut.clk)

    # Sustain spike for entire observation window so detect stays high
    buzzer_seen = False
    for _ in range(50000):
        dut.ui_in.value = 250
        await RisingEdge(dut.clk)
        if safe_read_bit(dut.uo_out, 1) == 1:
            buzzer_seen = True
            break

    assert buzzer_seen, "Buzzer output did not activate after target detection"
