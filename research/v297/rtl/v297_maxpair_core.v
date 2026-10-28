// Strong same-resource V297 control: exact maximum-cardinality feasible subset.
// Three requests, 16 banks, two RF read ports per bank, two issue slots.
// Ties favor oldest request(s). No additional RF ports or issue slots.
module v297_maxpair_core(
  input wire clk,
  input wire rst_n,
  input wire [2:0] valid,
  input wire [11:0] bank_a,
  input wire [11:0] bank_b,
  output wire [2:0] grant
);
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
  assign grant = p01 ? 3'b011 :
                 p02 ? 3'b101 :
                 p12 ? 3'b110 :
                 valid[0] ? 3'b001 :
                 valid[1] ? 3'b010 :
                 valid[2] ? 3'b100 : 3'b000;
endmodule
