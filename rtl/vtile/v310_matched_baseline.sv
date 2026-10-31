// V310 matched-I/O physical baseline: compact greedy unchanged, with the
// same 40 top-level input bits as the candidate. duplicate_verified is
// intentionally unused: this is the historical no-coalescing baseline.
// An actually reuse-capable hardware baseline remains a separate required
// control before novelty, area/power, or tile throughput can be claimed.
module vektor_v310_matched_baseline (
    input wire [3:0] request_valid,
    input wire [15:0] src0_bank_flat,
    input wire [15:0] src1_bank_flat,
    input wire [3:0] duplicate_verified,
    output wire [3:0] grant
);
    vektor_v310_compact_greedy_arbiter core (
        .request_valid(request_valid),
        .src0_bank_flat(src0_bank_flat),
        .src1_bank_flat(src1_bank_flat),
        .grant(grant)
    );
endmodule
