/*
 * Copyright (c) 2026 Illamparuthi
 * SPDX-License-Identifier: Apache-2.0
 */

`default_nettype none

module cfar_detector (
    input  wire       clk,
    input  wire       rst_n,
    input  wire [7:0] sample,
    output reg        detect
);

reg [7:0] w0,w1,w2,w3,w4,w5,w6,w7,w8,w9,w10;

// Shift register window
always @(posedge clk or negedge rst_n) begin
    if(!rst_n) begin
        w0  <= 8'd0;
        w1  <= 8'd0;
        w2  <= 8'd0;
        w3  <= 8'd0;
        w4  <= 8'd0;
        w5  <= 8'd0;
        w6  <= 8'd0;
        w7  <= 8'd0;
        w8  <= 8'd0;
        w9  <= 8'd0;
        w10 <= 8'd0;
        detect <= 1'b0;
    end
    else begin
        w10 <= w9;
        w9  <= w8;
        w8  <= w7;
        w7  <= w6;
        w6  <= w5;
        w5  <= w4;
        w4  <= w3;
        w3  <= w2;
        w2  <= w1;
        w1  <= w0;
        w0  <= sample;

        detect <= (w5 > threshold);
    end
end

// Training cell sum
wire [10:0] sum =
      w0 + w1 + w2 + w3 +
      w7 + w8 + w9 + w10;

// Noise estimate
wire [7:0] avg = sum >> 3;

// Threshold
wire [7:0] threshold = avg << 1;

endmodule
