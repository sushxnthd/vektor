// Equal-resource hardware-strength control for V297.
// Equivalent to phase-rotating serial greedy on every valid/compatibility
// combination, but uses static pair tests and constant-index priority muxes.
// No new read ports, issue slots, or extra lookahead. Three-way phase register.
// Unlike v297_bank_rescue_core ROTATING=1, this avoids variable part-selects.
module v297_rotating_static_core(
  input wire clk,
  input wire rst_n,
  input wire [2:0] valid,
  input wire [11:0] bank_a,
  input wire [11:0] bank_b,
  output wire [2:0] grant
);
  reg [1:0] phase;
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

  // A greedy serial arbiter first accepts the oldest valid request in
  // phase order, then accepts the first pair-compatible younger request.
  // If the first accepted request blocks both successors, it cannot
  // discard that first request to accept a compatible younger pair.
  wire [2:0] phase0 =
      p01 ? 3'b011 : p02 ? 3'b101 :
      valid[0] ? 3'b001 : p12 ? 3'b110 :
      valid[1] ? 3'b010 : valid[2] ? 3'b100 : 3'b000;
  wire [2:0] phase1 =
      p12 ? 3'b110 : p01 ? 3'b011 :
      valid[1] ? 3'b010 : p02 ? 3'b101 :
      valid[2] ? 3'b100 : valid[0] ? 3'b001 : 3'b000;
  wire [2:0] phase2 =
      p02 ? 3'b101 : p12 ? 3'b110 :
      valid[2] ? 3'b100 : p01 ? 3'b011 :
      valid[0] ? 3'b001 : valid[1] ? 3'b010 : 3'b000;
  assign grant = (phase==2'd0) ? phase0 :
                 (phase==2'd1) ? phase1 : phase2;

  always @(posedge clk or negedge rst_n)
    if (!rst_n) phase <= 2'd0;
    else phase <= (phase==2'd2) ? 2'd0 : phase+2'd1;
endmodule
