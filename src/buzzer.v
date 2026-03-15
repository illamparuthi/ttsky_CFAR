`default_nettype none

module buzzer_driver (
    input  wire clk,
    input  wire rst_n,
    input  wire detect,
    input  wire [7:0] strength,
    output reg  buzzer
);

// When detect pulses high (even briefly), latch and play a tone for
// HOLD_CYCLES clock cycles. This way a single CFAR detection event
// produces an audible beep regardless of how long detect stays high.
//
// At 10 MHz, HOLD_CYCLES=2000 → 0.2 ms beep (clearly audible in test).
// The tone toggles every HALF_PERIOD cycles within the hold window.
//   strength >= 80 → half_period = 250  → 20 kHz  (high pitch, strong target)
//   strength >= 40 → half_period = 500  → 10 kHz  (mid  pitch)
//   else           → half_period = 1000 →  5 kHz  (low  pitch, weak target)

localparam HOLD_CYCLES = 2000;

reg [11:0] hold_counter;   // counts down from HOLD_CYCLES to 0
reg [11:0] tone_counter;   // square wave divider within the hold
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
        // Re-trigger hold on any detect pulse
        if (detect)
            hold_counter <= HOLD_CYCLES;
        else if (hold_counter > 0)
            hold_counter <= hold_counter - 1;

        // Square wave generator active during hold
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
