/*
 * Copyright (c) 2026 Illamparuthi
 * SPDX-License-Identifier: Apache-2.0
 */

`default_nettype none

`ifdef USE_POWER_PINS
module cfar_detector (
    inout  wire       VPWR,
    inout  wire       VGND,
    input  wire       clk,
    input  wire       rst_n,
    input  wire [7:0] sample,
    output reg        detect,
    output reg  [7:0] strength
);
`else
module cfar_detector (
    input  wire       clk,
    input  wire       rst_n,
    input  wire [7:0] sample,
    output reg        detect,
    output reg  [7:0] strength
);
`endif

reg [7:0] w0,w1,w2,w3,w4,w5,w6,w7,w8,w9,w10;

wire [10:0] sum = {3'b0,w0} + {3'b0,w1} + {3'b0,w2} + {3'b0,w3}
                + {3'b0,w7} + {3'b0,w8} + {3'b0,w9} + {3'b0,w10};

wire [7:0] avg = sum[10:3];
wire [8:0] threshold = {avg, 1'b0};

always @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
        w0<=0; w1<=0; w2<=0; w3<=0; w4<=0;
        w5<=0; w6<=0; w7<=0; w8<=0; w9<=0; w10<=0;
        detect   <= 0;
        strength <= 0;
    end else begin
        w10 <= w9;  w9 <= w8;  w8 <= w7;  w7 <= w6;
        w6  <= w5;  w5 <= w4;  w4 <= w3;  w3 <= w2;
        w2  <= w1;  w1 <= w0;  w0 <= sample;
        detect   <= ({1'b0, w5} > threshold);
        strength <= avg;
    end
end

endmodule
