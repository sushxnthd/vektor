module vektor_rf_bank_arbiter #(
    parameter integer ISSUE_WIDTH = 4,
    parameter integer NUM_BANKS = 16,
    parameter integer BANK_ID_WIDTH = 4,
    parameter integer READ_PORTS_PER_BANK = 2
) (
    input  logic [ISSUE_WIDTH-1:0] request_valid,
    input  logic [ISSUE_WIDTH-1:0][BANK_ID_WIDTH-1:0] src0_bank,
    input  logic [ISSUE_WIDTH-1:0][BANK_ID_WIDTH-1:0] src1_bank,
    output logic [ISSUE_WIDTH-1:0] grant
);

    integer reads [0:NUM_BANKS-1];
    integer slot;
    integer bank;
    integer ok;

    always_comb begin
        grant = '0;
        for (bank = 0; bank < NUM_BANKS; bank = bank + 1)
            reads[bank] = 0;

        for (slot = 0; slot < ISSUE_WIDTH; slot = slot + 1) begin
            ok = 1;
            if (request_valid[slot]) begin
                if (src0_bank[slot] == src1_bank[slot]) begin
                    if ((reads[src0_bank[slot]] + 2) > READ_PORTS_PER_BANK)
                        ok = 0;
                end else begin
                    if ((reads[src0_bank[slot]] + 1) > READ_PORTS_PER_BANK)
                        ok = 0;
                    if ((reads[src1_bank[slot]] + 1) > READ_PORTS_PER_BANK)
                        ok = 0;
                end

                if (ok != 0) begin
                    grant[slot] = 1'b1;
                    reads[src0_bank[slot]] = reads[src0_bank[slot]] + 1;
                    reads[src1_bank[slot]] = reads[src1_bank[slot]] + 1;
                end
            end
        end
    end

endmodule
