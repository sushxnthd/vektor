// V317 equal-port maximum-cardinality RF arbiter CHALLENGER.
// Uncosted experimental alternative to rtl/vtile/rf_bank_arbiter.sv.
// Four slots, two independently charged reads per granted instruction,
// 16 banks, two physical reads per bank per cycle.
// No forwarding, operand-identity sharing or extra ports.
// Tie-break: numerically largest grant mask among maximum-cardinality sets.
module vektor_v317_rf_bank_exact (
    input  wire [3:0]  request_valid,
    input  wire [15:0] src0_bank_flat,
    input  wire [15:0] src1_bank_flat,
    output reg  [3:0]  grant
);
    integer candidate_id;
    integer bank_id;
    integer slot;
    integer reads;
    integer selected;
    integer best_selected;
    reg legal_candidate;
    reg [3:0] candidate_mask;
    reg [3:0] best_mask;

    always @* begin
        best_mask = 4'b0000;
        best_selected = -1;
        candidate_mask = 4'b0000;
        legal_candidate = 1'b0;
        reads = 0;
        selected = 0;
        for (candidate_id = 0; candidate_id < 16; candidate_id = candidate_id + 1) begin
            candidate_mask = candidate_id[3:0];
            legal_candidate = ((candidate_mask & ~request_valid) == 4'b0000);
            selected = 0;
            for (slot = 0; slot < 4; slot = slot + 1)
                if (candidate_mask[slot])
                    selected = selected + 1;
            for (bank_id = 0; bank_id < 16; bank_id = bank_id + 1) begin
                reads = 0;
                for (slot = 0; slot < 4; slot = slot + 1) begin
                    if (candidate_mask[slot]) begin
                        if (src0_bank_flat[slot*4 +: 4] == bank_id[3:0])
                            reads = reads + 1;
                        if (src1_bank_flat[slot*4 +: 4] == bank_id[3:0])
                            reads = reads + 1;
                    end
                end
                if (reads > 2)
                    legal_candidate = 1'b0;
            end
            if (legal_candidate && ((selected > best_selected) ||
                ((selected == best_selected) && (candidate_mask > best_mask)))) begin
                best_selected = selected;
                best_mask = candidate_mask;
            end
        end
        grant = best_mask;
    end
endmodule
