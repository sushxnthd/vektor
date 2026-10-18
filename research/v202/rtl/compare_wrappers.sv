// Identical four-request rotating greedy circuit; exchange output pruned by flattening.
// Only compare after Yosys reports independent optimized netlists.
module vektor_rf_greedy_only (
    input wire [3:0] request_valid,
    input wire [15:0] src0_bank_flat,
    input wire [15:0] src1_bank_flat,
    input wire [1:0] priority_turn,
    output wire [3:0] grant
);
  wire [3:0] unused_exchange;
  vektor_rf_exchange_arbiter core(
    .request_valid(request_valid),.src0_bank_flat(src0_bank_flat),
    .src1_bank_flat(src1_bank_flat),.priority_turn(priority_turn),
    .grant(unused_exchange),.greedy_grant(grant));
endmodule
module vektor_rf_exchange_only (
    input wire [3:0] request_valid,
    input wire [15:0] src0_bank_flat,
    input wire [15:0] src1_bank_flat,
    input wire [1:0] priority_turn,
    output wire [3:0] grant
);
  wire [3:0] unused_greedy;
  vektor_rf_exchange_arbiter core(
    .request_valid(request_valid),.src0_bank_flat(src0_bank_flat),
    .src1_bank_flat(src1_bank_flat),.priority_turn(priority_turn),
    .grant(grant),.greedy_grant(unused_greedy));
endmodule
