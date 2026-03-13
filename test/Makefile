# Makefile
# Cocotb simulation Makefile for TinyTapeout CFAR + Buzzer project

# Simulator
SIM ?= icarus
FST ?= -fst
TOPLEVEL_LANG ?= verilog

# Source directory
SRC_DIR = $(PWD)/../src

# Design files
PROJECT_SOURCES = project.v cfar.v buzzer.v

ifneq ($(GATES),yes)

# RTL simulation
SIM_BUILD = sim_build/rtl
VERILOG_SOURCES += $(addprefix $(SRC_DIR)/,$(PROJECT_SOURCES))

else

# Gate level simulation
SIM_BUILD = sim_build/gl

COMPILE_ARGS += -DGL_TEST
COMPILE_ARGS += -DFUNCTIONAL
COMPILE_ARGS += -DUSE_POWER_PINS
COMPILE_ARGS += -DSIM
COMPILE_ARGS += -DUNIT_DELAY=\#1

VERILOG_SOURCES += $(PDK_ROOT)/sky130A/libs.ref/sky130_fd_sc_hd/verilog/primitives.v
VERILOG_SOURCES += $(PDK_ROOT)/sky130A/libs.ref/sky130_fd_sc_hd/verilog/sky130_fd_sc_hd.v

# Gate-level netlist
VERILOG_SOURCES += $(PWD)/gate_level_netlist.v

endif

# Include directory for RTL
COMPILE_ARGS += -I$(SRC_DIR)

# Testbench
VERILOG_SOURCES += $(PWD)/tb.v
TOPLEVEL = tb

# Python test module
COCOTB_TEST_MODULES = test

# Cocotb make rules
include $(shell cocotb-config --makefiles)/Makefile.sim
