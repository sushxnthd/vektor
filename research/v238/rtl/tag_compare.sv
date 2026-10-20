// V238: tag-comparator input isolation. No power claim.
module v238_tag_match_baseline #(
  parameter integer TAG_W=8, PREFIX_W=3
)(
  input wire valid,
  input wire [TAG_W-1:0] return_tag, slot_tag,
  output wire match_o
);
  assign match_o = valid && (return_tag == slot_tag);
endmodule

module v238_tag_match_isolated #(
  parameter integer TAG_W=8, PREFIX_W=3
)(
  input wire valid,
  input wire [TAG_W-1:0] return_tag, slot_tag,
  output wire match_o
);
  localparam integer HI_W=TAG_W-PREFIX_W;
  wire pre_match = (return_tag[PREFIX_W-1:0] == slot_tag[PREFIX_W-1:0]);
  wire [HI_W-1:0] hi_return = return_tag[TAG_W-1:PREFIX_W] & {HI_W{pre_match}};
  wire [HI_W-1:0] hi_slot = slot_tag[TAG_W-1:PREFIX_W] & {HI_W{pre_match}};
  assign match_o = valid && pre_match && (hi_return == hi_slot);
endmodule
