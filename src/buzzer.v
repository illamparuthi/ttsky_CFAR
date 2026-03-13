`default_nettype none

module buzzer_driver (
    input  wire clk,
    input  wire rst_n,
    input  wire detect,
    input  wire [7:0] strength,
    output reg  buzzer
);

reg [23:0] counter;
reg [23:0] limit;

always @(*) begin
    if(strength < 8'd40)
        limit = 24'd5_000_000;
    else if(strength < 8'd80)
        limit = 24'd2_000_000;
    else
        limit = 24'd500_000;
end

always @(posedge clk or negedge rst_n) begin
    if(!rst_n) begin
        counter <= 0;
        buzzer <= 0;
    end
    else if(detect) begin
        counter <= counter + 1;

        if(counter >= limit) begin
            buzzer <= ~buzzer;
            counter <= 0;
        end
    end
    else begin
        counter <= 0;
        buzzer <= 0;
    end
end

endmodule
