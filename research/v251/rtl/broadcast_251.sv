module v251_locality_broadcast(
  input logic [31:0] operand, consumer_mask,
  input logic [1:0] source_quadrant,
  output logic global_trunk_enable,
  output logic [1023:0] lane_operands
);
  logic [31:0] remote_mask;
  always_comb begin
    remote_mask = consumer_mask & ~(32'hff << (8 * source_quadrant));
    global_trunk_enable = |remote_mask;
    for (int i=0;i<32;i++)
      lane_operands[32*i +: 32] = consumer_mask[i] ? operand : 32'b0;
  end
endmodule
module v251_matched_control(
  input logic [31:0] operand, consumer_mask,
  input logic [1:0] source_quadrant,
  output logic global_trunk_enable,
  output logic [1023:0] lane_operands
);
  always_comb begin
    global_trunk_enable = |(consumer_mask & ~(32'hff << (8 * source_quadrant)));
    for (int i=0;i<32;i++)
      lane_operands[32*i +: 32] = {32{consumer_mask[i]}} & operand;
  end
endmodule
