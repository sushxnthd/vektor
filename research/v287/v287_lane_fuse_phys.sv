module v287_lane_fuse_phys #(
  parameter LANES=8, W=32, AW=12
)(
  input wire [LANES-1:0] mask_a, mask_b,
  input wire [1:0] op_a, op_b,
  input wire [LANES*W-1:0] lhs_a, rhs_a, lhs_b, rhs_b,
  input wire [LANES*AW-1:0] dst_a, dst_b,
  output wire fused, retire_a, retire_b,
  output wire [LANES-1:0] wen,
  output wire [LANES*W-1:0] wdata,
  output wire [LANES*AW-1:0] waddr
);
  wire valid_a = (|mask_a) && (op_a == 0);
  assign fused = valid_a && (|mask_b) && (op_b == 0) &&
                 ((mask_a & mask_b) == 0);
  assign retire_a = valid_a;
  assign retire_b = fused;
  genvar i;
  generate for (i=0; i<LANES; i=i+1) begin: lane
    wire take_b = fused && mask_b[i];
    wire [W-1:0] x = take_b ? lhs_b[i*W+:W] : lhs_a[i*W+:W];
    wire [W-1:0] y = take_b ? rhs_b[i*W+:W] : rhs_a[i*W+:W];
    assign wen[i] = (valid_a && mask_a[i]) || take_b;
    assign wdata[i*W+:W] = x + y;
    assign waddr[i*AW+:AW] = take_b ? dst_b[i*AW+:AW] : dst_a[i*AW+:AW];
  end endgenerate
endmodule
