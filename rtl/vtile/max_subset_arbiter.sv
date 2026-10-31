// V309 exploratory successor: exact maximum-cardinality admission.
// This intentionally straightforward combinational enumeration is a physicality
// prefilter, NOT a timing-closed or novel GPU scheduler. Two reads per request,
// including two reads when the two bank IDs are equal.
module vektor_v309_max_subset_arbiter (
    input  wire [3:0]  request_valid,
    input  wire [15:0] src0_bank_flat,
    input  wire [15:0] src1_bank_flat,
    output reg  [3:0]  grant
);
    integer subset;
    integer slot;
    integer bank;
    reg [3:0] subset_mask;
    reg [3:0] port_demand;
    reg [2:0] issue_count;
    reg [2:0] best_count;
    reg admissible;

    always @* begin
        grant = 4'b0000;
        best_count = 3'd0;
        subset_mask = 4'b0000;
        port_demand = 4'd0;
        issue_count = 3'd0;
        admissible = 1'b0;

        // Ascending masks + strict score comparison implement a fixed,
        // reproducible smallest-numeric-mask tie break.
        for (subset = 0; subset < 16; subset = subset + 1) begin
            subset_mask = subset[3:0];
            admissible = ((subset_mask & ~request_valid) == 4'b0000);
            issue_count = 3'd0;
            for (slot = 0; slot < 4; slot = slot + 1) begin
                if (subset_mask[slot])
                    issue_count = issue_count + 3'd1;
            end

            for (bank = 0; bank < 16; bank = bank + 1) begin
                port_demand = 4'd0;
                for (slot = 0; slot < 4; slot = slot + 1) begin
                    if (subset_mask[slot]) begin
                        if (src0_bank_flat[slot*4 +: 4] == bank[3:0])
                            port_demand = port_demand + 4'd1;
                        if (src1_bank_flat[slot*4 +: 4] == bank[3:0])
                            port_demand = port_demand + 4'd1;
                    end
                end
                if (port_demand > 4'd2)
                    admissible = 1'b0;
            end

            if (admissible && issue_count > best_count) begin
                best_count = issue_count;
                grant = subset_mask;
            end
        end
    end
endmodule
