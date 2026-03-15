# Makefile
# Cocotb simulation Makefile for TinyTapeout CFAR + Buzzer project

SIM          ?= icarus
TOPLEVEL_LANG ?= verilog

SRC_DIR = $(PWD)/../src

PROJECT_SOURCES = project.v cfar.v buzzer.v

ifneq ($(GATES),yes)

# ── RTL simulation ────────────────────────────────────────────────
SIM_BUILD        = sim_build/rtl
VERILOG_SOURCES += $(addprefix $(SRC_DIR)/,$(PROJECT_SOURCES))
TOPLEVEL         = tt_um_ttsky_cfar

else

# ── Gate-level simulation ─────────────────────────────────────────
SIM_BUILD        = sim_build/gl

COMPILE_ARGS    += -DGL_TEST
COMPILE_ARGS    += -DFUNCTIONAL
COMPILE_ARGS    += -DUSE_POWER_PINS
COMPILE_ARGS    += -DSIM
COMPILE_ARGS    += -DUNIT_DELAY=\#1

VERILOG_SOURCES += $(PDK_ROOT)/sky130A/libs.ref/sky130_fd_sc_hd/verilog/primitives.v
VERILOG_SOURCES += $(PDK_ROOT)/sky130A/libs.ref/sky130_fd_sc_hd/verilog/sky130_fd_sc_hd.v

# CI copies the netlist to this exact path (cp tt_submission/*.v test/gate_level_netlist.v)
VERILOG_SOURCES += $(PWD)/gate_level_netlist.v

TOPLEVEL         = tt_um_ttsky_cfar

endif

COMPILE_ARGS    += -I$(SRC_DIR)

# Python test module (filename without .py)
MODULE           = test

include $(shell cocotb-config --makefiles)/Makefile.sim
