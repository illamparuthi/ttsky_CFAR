`default_nettype none

module buzzer_driver (
    input  wire clk,
    input  wire rst_n,
    input  wire detect,
    input  wire [7:0] strength,
    output reg  buzzer
);

// Counter width: 24 bits (max ~16M)
// Limits chosen so buzzer toggles within ~1000 cycles for simulation
// and produces audible tones at 10 MHz in hardware:
//   strength < 40  → ~3 kHz  (limit = 1667)
//   strength < 80  → ~5 kHz  (limit = 1000)
//   else           → ~10 kHz (limit =  500)
reg [23:0] counter;
reg [23:0] limit;

always @(*) begin
    if (strength < 8'd40)
        limit = 24'd1667;
    else if (strength < 8'd80)
        limit = 24'd1000;
    else
        limit = 24'd500;
end

always @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
        counter <= 0;
        buzzer  <= 0;
    end
    else if (detect) begin
        if (counter >= limit) begin
            buzzer  <= ~buzzer;
            counter <= 0;
        end else begin
            counter <= counter + 1;
        end
    end
    else begin
        counter <= 0;
        buzzer  <= 0;
    end
end

endmodule
