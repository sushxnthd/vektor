// Saturating ready-response age counter. AGE_LIMIT must fit in AGEW bits.
module rf_sat_age_058 #(parameter AGEW=3, AGE_LIMIT=4)(
 input wire clk, input wire rst_n,
 input wire allocate, input wire release, input wire wait_cycle,
 output reg [AGEW-1:0] age
);
 always @(posedge clk) begin
   if (!rst_n || release || allocate) age <= 0;
   else if (wait_cycle && age < AGE_LIMIT) age <= age + 1'b1;
 end
endmodule
