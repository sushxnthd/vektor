// V286: physical RF bank mapping, must be used consistently on reads/writes.
// No storage or port changes. This is NOT a complete RF implementation.
module v286_add_bank_map(
 input wire [3:0] logical_bank,
 input wire [3:0] warp_id_low,
 output wire [3:0] physical_bank
);
 assign physical_bank=logical_bank+warp_id_low;
endmodule
module v286_xor_bank_map(
 input wire [3:0] logical_bank,
 input wire [3:0] warp_id_low,
 output wire [3:0] physical_bank
);
 assign physical_bank=logical_bank^warp_id_low;
endmodule
