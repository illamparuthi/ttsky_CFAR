# SPDX-FileCopyrightText: © 2024 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0


import cocotb
from cocotb.triggers import RisingEdge
from cocotb.clock import Clock


@cocotb.test()
async def test_project(dut):

    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())

    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.rst_n.value = 0

    # reset
    for _ in range(5):
        await RisingEdge(dut.clk)

    dut.rst_n.value = 1

    # feed noise samples
    for val in [10, 11, 9, 10, 12, 11, 10]:
        dut.ui_in.value = val
        await RisingEdge(dut.clk)

    # strong reflection
    dut.ui_in.value = 80
    await RisingEdge(dut.clk)

    # allow pipeline to update
    for _ in range(10):
        await RisingEdge(dut.clk)

    # detect should eventually be 1
    assert dut.uo_out.value != 0
