/*
 * Copyright (c) 2026 illamparuthi
 * SPDX-License-Identifier: Apache-2.0
 */

`default_nettype none

`ifdef USE_POWER_PINS
module tt_um_ttsky_cfar (
    input  wire [7:0] ui_in,
    output wire [7:0] uo_out,
    input  wire [7:0] uio_in,
    output wire [7:0] uio_out,
    output wire [7:0] uio_oe,
    input  wire       ena,
    input  wire       clk,
    input  wire       rst_n,
    inout  wire       VPWR,
    inout  wire       VGND
);
`else
module tt_um_ttsky_cfar (
    input  wire [7:0] ui_in,
    output wire [7:0] uo_out,
    input  wire [7:0] uio_in,
    output wire [7:0] uio_out,
    output wire [7:0] uio_oe,
    input  wire       ena,
    input  wire       clk,
    input  wire       rst_n
);
`endif

wire detect;
wire buzzer;
wire [7:0] strength;

cfar_detector cfar (
`ifdef USE_POWER_PINS
    .VPWR(VPWR),
    .VGND(VGND),
`endif
    .clk(clk),
    .rst_n(rst_n),
    .sample(ui_in),
    .detect(detect),
    .strength(strength)
);

buzzer_driver buzz (
`ifdef USE_POWER_PINS
    .VPWR(VPWR),
    .VGND(VGND),
`endif
    .clk(clk),
    .rst_n(rst_n),
    .detect(detect),
    .strength(strength),
    .buzzer(buzzer)
);

assign uo_out  = {6'b0, buzzer, detect};
assign uio_out = 8'b0;
assign uio_oe  = 8'b0;

wire _unused = &{ena, uio_in, 1'b0};

endmodule
