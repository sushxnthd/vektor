// V287 equal-port one-warp issue control: same 8x32b ALUs, per-lane RF ports,
// identical interface, one warp retirement per cycle, no operand/address mux.
module v287_lane_control #(
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
 wire valid_a = (|mask_a) && (op_a == 2'b00);
 assign fused=1'b0;
 assign retire_a=valid_a;
 assign retire_b=1'b0;
 genvar i;
 generate for(i=0;i<LANES;i=i+1) begin:lane
   assign wen[i]=valid_a && mask_a[i];
   assign wdata[i*W+:W]=lhs_a[i*W+:W]+rhs_a[i*W+:W];
   assign waddr[i*AW+:AW]=dst_a[i*AW+:AW];
 end endgenerate
endmodule
