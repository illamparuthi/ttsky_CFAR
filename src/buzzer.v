`default_nettype none

`ifdef USE_POWER_PINS
module buzzer_driver (
    inout  wire       VPWR,
    inout  wire       VGND,
    input  wire       clk,
    input  wire       rst_n,
    input  wire       detect,
    input  wire [7:0] strength,
    output reg        buzzer
);
`else
module buzzer_driver (
    input  wire       clk,
    input  wire       rst_n,
    input  wire       detect,
    input  wire [7:0] strength,
    output reg        buzzer
);
`endif

localparam HOLD_CYCLES = 2000;

reg [11:0] hold_counter;
reg [11:0] tone_counter;
reg [11:0] half_period;

always @(*) begin
    if (strength >= 8'd80)
        half_period = 12'd250;
    else if (strength >= 8'd40)
        half_period = 12'd500;
    else
        half_period = 12'd1000;
end

always @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
        hold_counter <= 0;
        tone_counter <= 0;
        buzzer       <= 0;
    end else begin
        if (detect)
            hold_counter <= HOLD_CYCLES;
        else if (hold_counter > 0)
            hold_counter <= hold_counter - 1;

        if (hold_counter > 0) begin
            if (tone_counter >= half_period) begin
                buzzer       <= ~buzzer;
                tone_counter <= 0;
            end else begin
                tone_counter <= tone_counter + 1;
            end
        end else begin
            buzzer       <= 0;
            tone_counter <= 0;
        end
    end
end

endmodule
