// Matched registered boundary for V297 physical kill experiment.
// Exactly identical input/output registers, RF ports, issue slots and clock
// for compact cooldown, unrestricted max-pair and optimized rotating serial.
// This shell is an arbiter test macro, NOT an integrated GPU tile.
module v297_matched_shell #(
  parameter integer POLICY = 0
)(
  input wire clk,
  input wire rst_n,
  input wire [2:0] valid,
  input wire [11:0] bank_a,
  input wire [11:0] bank_b,
  output reg [2:0] grant
);
  reg [2:0] valid_q;
  reg [11:0] bank_a_q, bank_b_q;
  wire [2:0] internal_grant;
  generate
    if (POLICY == 0) begin: compact
      v297_maxpair_cooldown_core core(
        .clk(clk),.rst_n(rst_n),.valid(valid_q),
        .bank_a(bank_a_q),.bank_b(bank_b_q),.grant(internal_grant));
    end else if (POLICY == 1) begin: maxpair
      v297_maxpair_core core(
        .clk(clk),.rst_n(rst_n),.valid(valid_q),
        .bank_a(bank_a_q),.bank_b(bank_b_q),.grant(internal_grant));
    end else if (POLICY == 2) begin: rotating
      v297_rotating_static_core core(
        .clk(clk),.rst_n(rst_n),.valid(valid_q),
        .bank_a(bank_a_q),.bank_b(bank_b_q),.grant(internal_grant));
    end else begin: invalid_policy
      initial $fatal(1,"Invalid POLICY");
    end
  endgenerate
  always @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
      valid_q <= 0;
      bank_a_q <= 0;
      bank_b_q <= 0;
      grant <= 0;
    end else begin
      valid_q <= valid;
      bank_a_q <= bank_a;
      bank_b_q <= bank_b;
      grant <= internal_grant;
    end
  end
endmodule
