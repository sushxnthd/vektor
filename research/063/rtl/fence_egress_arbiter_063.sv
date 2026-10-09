// Vektor-063 single-lane DATA / FENCE_ACK arbiter.
// Inputs must hold valid and payload until ready handshake.
// The fabric must generate a *strong* quiescence ACK; this module does not.
module fence_egress_arbiter_063 #(
  parameter integer TAGW=8,
  parameter integer ACK_FIRST=1
)(
  input wire clk, rst,
  input wire data_valid,
  output wire data_ready,
  input wire [TAGW-1:0] data_tag,
  input wire ack_valid,
  output wire ack_ready,
  input wire [TAGW-1:0] ack_tag,
  output wire out_valid,
  input wire out_ready,
  output wire out_is_ack,
  output wire [TAGW-1:0] out_tag
);
  reg locked;
  reg locked_ack;
  wire choose_ack = locked ? locked_ack :
      (ACK_FIRST ? ack_valid : (!data_valid && ack_valid));
  assign out_is_ack = choose_ack;
  assign out_valid = choose_ack ? ack_valid : data_valid;
  assign out_tag = choose_ack ? ack_tag : data_tag;
  assign ack_ready = out_ready && out_valid && choose_ack;
  assign data_ready = out_ready && out_valid && !choose_ack;
  always @(posedge clk) begin
    if (rst) begin
      locked <= 1'b0;
      locked_ack <= 1'b0;
    end else if (out_valid && !out_ready && !locked) begin
      locked <= 1'b1;
      locked_ack <= choose_ack;
    end else if (out_valid && out_ready) begin
      locked <= 1'b0;
    end
  end
endmodule
