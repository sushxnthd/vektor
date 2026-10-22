// Conventional operand-collector read broadcast: strongest same-budget V291 control.
// One physical RF read port; no added storage, bank ports or response bandwidth.
// All tags encode complete physical register identity including warp/version.
module v291_equal_budget_broadcast #(parameter TAG_W=8, DATA_W=32)(
  input wire [3:0] valid,
  input wire [4*TAG_W-1:0] tag,
  input wire [DATA_W-1:0] rf_data,
  output wire rf_read,
  output wire [TAG_W-1:0] rf_tag,
  output wire [3:0] served,
  output wire [4*DATA_W-1:0] consumer_data
);
  wire [3:0] select_first;
  assign select_first[0] = valid[0];
  assign select_first[1] = valid[1] & ~valid[0];
  assign select_first[2] = valid[2] & ~(|valid[1:0]);
  assign select_first[3] = valid[3] & ~(|valid[2:0]);
  assign rf_read = |valid;
  assign rf_tag =
      (tag[0*TAG_W +: TAG_W] & {TAG_W{select_first[0]}})
    | (tag[1*TAG_W +: TAG_W] & {TAG_W{select_first[1]}})
    | (tag[2*TAG_W +: TAG_W] & {TAG_W{select_first[2]}})
    | (tag[3*TAG_W +: TAG_W] & {TAG_W{select_first[3]}});
  genvar k;
  generate for (k=0; k<4; k=k+1) begin: lane
    assign served[k] = valid[k] & rf_read &
      (tag[k*TAG_W +: TAG_W] == rf_tag);
    assign consumer_data[k*DATA_W +: DATA_W] =
      rf_data & {DATA_W{served[k]}};
  end endgenerate
endmodule
