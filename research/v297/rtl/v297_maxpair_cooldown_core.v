// Same V297 grants and cooldown, but direct pairwise-feasibility logic.
// This is an implementation-strength control, NOT a new architecture mechanism.
module v297_maxpair_cooldown_core(
  input wire clk,
  input wire rst_n,
  input wire [2:0] valid,
  input wire [11:0] bank_a,
  input wire [11:0] bank_b,
  output wire [2:0] grant
);
  reg cooldown;
  function automatic fits_pair;
    input [3:0] a,b,c,d;
    begin
      fits_pair = !((a==b && a==c) ||
                    (a==b && a==d) ||
                    (a==c && a==d) ||
                    (b==c && b==d));
    end
  endfunction
  wire p01 = valid[0] && valid[1] &&
      fits_pair(bank_a[3:0],bank_b[3:0],bank_a[7:4],bank_b[7:4]);
  wire p02 = valid[0] && valid[2] &&
      fits_pair(bank_a[3:0],bank_b[3:0],bank_a[11:8],bank_b[11:8]);
  wire p12 = valid[1] && valid[2] &&
      fits_pair(bank_a[7:4],bank_b[7:4],bank_a[11:8],bank_b[11:8]);
  wire rescue = valid[0] && p12 && !p01 && !p02 && !cooldown;
  assign grant = p01 ? 3'b011 :
                 p02 ? 3'b101 :
                 p12 ? ((valid[0] && cooldown) ? 3'b001 : 3'b110) :
                 valid[0] ? 3'b001 :
                 valid[1] ? 3'b010 :
                 valid[2] ? 3'b100 : 3'b000;
  always @(posedge clk or negedge rst_n)
    if(!rst_n) cooldown<=1'b0;
    else cooldown<=rescue;
endmodule
