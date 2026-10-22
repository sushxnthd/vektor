// V292 isolated combinational return overlay. E0 ONLY: no timing, cacheline or
// collector port claims. One existing 1024-bit bus, two existing collectors.
module v292_sparse_return_overlay #(
  parameter LANES=32, DATA_W=32, TAG_W=16
)(
  input wire valid_a, valid_b,
  input wire [1:0] collector_credits,
  input wire [LANES-1:0] mask_a, mask_b,
  input wire [LANES*DATA_W-1:0] data_a, data_b,
  input wire [TAG_W-1:0] tag_a, tag_b,
  output wire accept_a, accept_b,
  output wire [LANES*DATA_W-1:0] data_out,
  output wire [LANES-1:0] out_mask_a, out_mask_b,
  output wire [TAG_W-1:0] out_tag_a, out_tag_b
);
  wire disjoint = ~|(mask_a & mask_b);
  assign accept_a = valid_a && (collector_credits != 0);
  assign accept_b = accept_a && valid_b && disjoint && (collector_credits >= 2);
  assign out_mask_a = accept_a ? mask_a : {LANES{1'b0}};
  assign out_mask_b = accept_b ? mask_b : {LANES{1'b0}};
  assign out_tag_a = accept_a ? tag_a : {TAG_W{1'b0}};
  assign out_tag_b = accept_b ? tag_b : {TAG_W{1'b0}};
  genvar k;
  generate for(k=0;k<LANES;k=k+1) begin: lane
    assign data_out[k*DATA_W +: DATA_W] =
       (accept_a && mask_a[k]) ? data_a[k*DATA_W +: DATA_W] :
       (accept_b && mask_b[k]) ? data_b[k*DATA_W +: DATA_W] :
       {DATA_W{1'b0}};
  end endgenerate
endmodule
