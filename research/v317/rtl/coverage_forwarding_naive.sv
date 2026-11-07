// V317 fail-closed coverage contract around the existing stateful snapshot.
// coverage_ok MUST come from an independent, complete write-observation
// authority. This module cannot detect a missed write if coverage_ok stays 1.
// A gap poisons the current snapshot until a clean recapture.
module vektor_v317_coverage_forwarding_naive #(
    parameter integer WARP_BITS = 2,
    parameter integer REG_BITS = 4,
    parameter integer BANK_BITS = 2,
    parameter integer LANES = 4,
    parameter integer DATA_BITS = 8
) (
    input wire clk, rst_n, coverage_ok, capture_en,
    input wire [WARP_BITS-1:0] capture_warp,
    input wire [REG_BITS-1:0] capture_reg,
    input wire [BANK_BITS-1:0] capture_bank,
    input wire [LANES-1:0] capture_lanes,
    input wire [LANES*DATA_BITS-1:0] capture_data,
    input wire write_en,
    input wire [WARP_BITS-1:0] write_warp,
    input wire [REG_BITS-1:0] write_reg,
    input wire [BANK_BITS-1:0] write_bank,
    input wire [LANES-1:0] write_lanes,
    input wire [WARP_BITS-1:0] requested_warp,
    input wire [REG_BITS-1:0] requested_reg,
    input wire [BANK_BITS-1:0] requested_bank,
    input wire [LANES-1:0] requested_lanes,
    output wire forward_grant,
    output wire [LANES*DATA_BITS-1:0] forwarded_data
);
    reg coverage_fault_q;
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n)
            coverage_fault_q <= 1'b1;
        else if (capture_en)
            coverage_fault_q <= !coverage_ok;
        else if (!coverage_ok)
            coverage_fault_q <= 1'b1;
    end

    wire underlying_grant;
    wire [LANES*DATA_BITS-1:0] underlying_data;
    vektor_v317_stateful_forwarding #(
        .WARP_BITS(WARP_BITS), .REG_BITS(REG_BITS),
        .BANK_BITS(BANK_BITS), .LANES(LANES), .DATA_BITS(DATA_BITS)
    ) snapshot (
        .clk(clk), .rst_n(rst_n),
        .capture_en(capture_en), .capture_warp(capture_warp),
        .capture_reg(capture_reg), .capture_bank(capture_bank),
        .capture_lanes(capture_lanes), .capture_data(capture_data),
        .write_en(write_en), .write_warp(write_warp),
        .write_reg(write_reg), .write_bank(write_bank),
        .write_lanes(write_lanes),
        .requested_warp(requested_warp), .requested_reg(requested_reg),
        .requested_bank(requested_bank), .requested_lanes(requested_lanes),
        .forward_grant(underlying_grant), .forwarded_data(underlying_data)
    );
    assign forward_grant = underlying_grant && coverage_ok && !coverage_fault_q;
    assign forwarded_data = forward_grant
        ? underlying_data : {(LANES*DATA_BITS){1'b0}};
endmodule
