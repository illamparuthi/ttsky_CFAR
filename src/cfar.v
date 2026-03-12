/*
 * Copyright (c) 2026 Your Name
 * SPDX-License-Identifier: Apache-2.0
 */

`default_nettype none

module cfar_detector (
    input  wire       clk,
    input  wire       rst_n,
    input  wire [7:0] sample,
    output reg        detect
);

    // Sliding window to store recent radar samples
    reg [7:0] window [0:10];
    integer i;

    // Shift register logic
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            for (i = 0; i < 11; i = i + 1) begin
                window[i] <= 8'd0;
            end
        end else begin
            for (i = 10; i > 0; i = i - 1) begin
                window[i] <= window[i-1];
            end
            window[0] <= sample;
        end
    end

    // Cell Under Test (CUT)
    wire [7:0] CUT = window[5];

    // Sum of training cells (excluding guard cells and CUT)
    wire [10:0] sum =
          window[0] + window[1] + window[2] + window[3] +
          window[7] + window[8] + window[9] + window[10];

    // Noise average and threshold generation
    wire [7:0] avg       = sum >> 3;   // divide by 8
    wire [7:0] threshold = avg << 1;   // multiply by 2

    // Detection logic
    always @(posedge clk) begin
        detect <= (CUT > threshold);
    end

endmodule
