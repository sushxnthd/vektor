// V286 one-repair hash: rotate warp-id bits before XOR with logical RF bank.
// The permutation is wiring only. Must be used consistently for read AND write.
module v286_permuted_bank_map(
 input wire [3:0] logical_bank,
 input wire [3:0] warp_id_low,
 output wire [3:0] physical_bank
);
 assign physical_bank=logical_bank ^ {warp_id_low[2:0],warp_id_low[3]};
endmodule
