`timescale 1ns/1ps
`default_nettype none

module tb;

reg clk;
reg rst_n;
reg [7:0] sample;
wire detect;

// Instantiate DUT
cfar_detector dut (
    .clk(clk),
    .rst_n(rst_n),
    .sample(sample),
    .detect(detect)
);

// Clock generator (100 MHz)
always #5 clk = ~clk;

initial begin
    $dumpfile("cfar_tb.vcd");
    $dumpvars(0, tb);

    clk = 0;
    rst_n = 0;
    sample = 0;

    // Reset
    #20;
    rst_n = 1;

    // Background noise samples
    repeat(10) begin
        @(posedge clk);
        sample = 8'd10;
    end

    // Slight variation noise
    @(posedge clk); sample = 8'd11;
    @(posedge clk); sample = 8'd9;
    @(posedge clk); sample = 8'd10;

    // Strong reflection (target)
    @(posedge clk); sample = 8'd80;

    // Return to noise
    @(posedge clk); sample = 8'd11;
    @(posedge clk); sample = 8'd10;

    // Wait some cycles
    repeat(10) @(posedge clk);

    $finish;
end

endmodule
