// V317 matched physical wrapper: one-cycle input and output register boundaries.
// Both variants have exactly 36 input FFs and 4 output FFs, no extra RF ports.
// The only difference is the grant-equivalent combinational core.
// This is a CONTROL BLOCK, not a complete GPU issue tile.
module vektor_v317_rf_physical_top_source (
    input wire clk,
    input wire [3:0] request_valid,
    input wire [15:0] src0_bank_flat,
    input wire [15:0] src1_bank_flat,
    output wire [3:0] grant
);
    reg [3:0] valid_q;
    reg [15:0] src0_q, src1_q;
    reg [3:0] grant_q;
    wire [3:0] core_grant;
    always @(posedge clk) begin
        valid_q <= request_valid;
        src0_q <= src0_bank_flat;
        src1_q <= src1_bank_flat;
        grant_q <= core_grant;
    end
    vektor_rf_bank_arbiter core (
        .request_valid(valid_q), .src0_bank_flat(src0_q),
        .src1_bank_flat(src1_q), .grant(core_grant)
    );
    assign grant = grant_q;
endmodule

module vektor_v317_rf_physical_top_pairwise (
    input wire clk,
    input wire [3:0] request_valid,
    input wire [15:0] src0_bank_flat,
    input wire [15:0] src1_bank_flat,
    output wire [3:0] grant
);
    reg [3:0] valid_q;
    reg [15:0] src0_q, src1_q;
    reg [3:0] grant_q;
    wire [3:0] core_grant;
    always @(posedge clk) begin
        valid_q <= request_valid;
        src0_q <= src0_bank_flat;
        src1_q <= src1_bank_flat;
        grant_q <= core_grant;
    end
    vektor_v317_rf_pairwise core (
        .request_valid(valid_q), .src0_bank_flat(src0_q),
        .src1_bank_flat(src1_q), .grant(core_grant)
    );
    assign grant = grant_q;
endmodule
