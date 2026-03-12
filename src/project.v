/*
 * Copyright (c) 2026 illamparuthi
 * SPDX-License-Identifier: Apache-2.0
 */

`default_nettype none

module tt_um_ttsky_CFAR (
    input  wire [7:0] ui_in,    // Dedicated inputs (radar samples)
    output wire [7:0] uo_out,   // Dedicated outputs
    input  wire [7:0] uio_in,   // IOs: Input path (unused)
    output wire [7:0] uio_out,  // IOs: Output path
    output wire [7:0] uio_oe,   // IOs: Enable path
    input  wire       ena,      // always 1 when powered
    input  wire       clk,      // clock
    input  wire       rst_n     // reset
);

    wire detect;

    // Instantiate CFAR core
    cfar_detector cfar_inst (
        .clk(clk),
        .rst_n(rst_n),
        .sample(ui_in),
        .detect(detect)
    );

    // Output mapping
    assign uo_out[0] = detect;
    assign uo_out[7:1] = 7'b0;

    // Unused bidirectional IOs
    assign uio_out = 8'b0;
    assign uio_oe  = 8'b0;

    // Prevent unused signal warnings
    wire _unused = &{ena, uio_in, 1'b0};

endmodule
