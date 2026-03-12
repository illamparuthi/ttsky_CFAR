`default_nettype none
`timescale 1ns / 1ps

/* 
   TinyTapeout testbench
   Instantiates the user project and exposes signals for cocotb tests
*/

module tb ();

  // Dump waveform file
  initial begin
    $dumpfile("tb.fst");
    $dumpvars(0, tb);
    #1;
  end

  // Inputs
  reg clk;
  reg rst_n;
  reg ena;
  reg [7:0] ui_in;
  reg [7:0] uio_in;

  // Outputs
  wire [7:0] uo_out;
  wire [7:0] uio_out;
  wire [7:0] uio_oe;

`ifdef GL_TEST
  wire VPWR = 1'b1;
  wire VGND = 1'b0;
`endif

  // Instantiate the user project
  tt_um_ttsky_CFAR user_project (

`ifdef GL_TEST
      .VPWR(VPWR),
      .VGND(VGND),
`endif

      .ui_in  (ui_in),    // radar samples input
      .uo_out (uo_out),   // detection output
      .uio_in (uio_in),   // unused
      .uio_out(uio_out),
      .uio_oe (uio_oe),
      .ena    (ena),
      .clk    (clk),
      .rst_n  (rst_n)
  );

  // Simple clock generator
  initial begin
    clk = 0;
    forever #5 clk = ~clk;
  end

  // Basic stimulus
  initial begin

    ena = 1;
    rst_n = 0;
    ui_in = 0;
    uio_in = 0;

    #20;
    rst_n = 1;

    // Simulated radar samples
    #10 ui_in = 8'd10;
    #10 ui_in = 8'd12;
    #10 ui_in = 8'd11;
    #10 ui_in = 8'd9;
    #10 ui_in = 8'd10;

    // strong reflection (target)
    #10 ui_in = 8'd80;

    // back to noise
    #10 ui_in = 8'd11;
    #10 ui_in = 8'd10;

    #100;
    $finish;

  end

endmodule
