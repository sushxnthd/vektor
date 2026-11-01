// V317 stateful single-entry source snapshot and sticky write monitor.
// Safety contract: capture_data is a coherent immutable snapshot; every
// intervening physical write must appear at write_* inputs. A same-cycle
// write to a requested lane blocks forwarding even before the clock edge.
// This is a correctness experiment, NOT a novel GPU architecture claim.
module vektor_v317_stateful_forwarding #(
    parameter integer WARP_BITS = 2,
    parameter integer REG_BITS = 4,
    parameter integer BANK_BITS = 2,
    parameter integer LANES = 4,
    parameter integer DATA_BITS = 8,
    parameter integer COVERAGE_GUARD = 0
) (
    input wire clk,
    input wire rst_n,
    input wire coverage_ok,
    input wire coverage_fault,
    input wire capture_en,
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
    reg valid_q;
    reg [WARP_BITS-1:0] warp_q;
    reg [REG_BITS-1:0] reg_q;
    reg [BANK_BITS-1:0] bank_q;
    reg [LANES-1:0] captured_q;
    reg [LANES-1:0] dirty_q;
    reg [LANES*DATA_BITS-1:0] data_q;

    wire write_hits_old = write_en && valid_q
        && write_warp == warp_q
        && write_reg == reg_q
        && write_bank == bank_q;
    wire write_hits_capture = write_en
        && write_warp == capture_warp
        && write_reg == capture_reg
        && write_bank == capture_bank;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            valid_q <= 1'b0;
            warp_q <= {WARP_BITS{1'b0}};
            reg_q <= {REG_BITS{1'b0}};
            bank_q <= {BANK_BITS{1'b0}};
            captured_q <= {LANES{1'b0}};
            dirty_q <= {LANES{1'b0}};
            data_q <= {(LANES*DATA_BITS){1'b0}};
        end else if (capture_en) begin
            valid_q <= 1'b1;
            warp_q <= capture_warp;
            reg_q <= capture_reg;
            bank_q <= capture_bank;
            captured_q <= capture_lanes;
            data_q <= capture_data;
            // Capture/write ordering is unspecified: fail closed on overlap.
            dirty_q <= write_hits_capture
                ? (capture_lanes & write_lanes) : {LANES{1'b0}};
        end else if (write_hits_old) begin
            dirty_q <= dirty_q | write_lanes;
        end
    end

    wire raw_grant;
    wire [LANES*DATA_BITS-1:0] raw_data;
    vektor_v317_forwarding_gate #(
        .WARP_BITS(WARP_BITS), .REG_BITS(REG_BITS),
        .BANK_BITS(BANK_BITS), .LANES(LANES), .DATA_BITS(DATA_BITS)
    ) gate (
        .cached_valid(valid_q), .cached_warp(warp_q),
        .cached_reg(reg_q), .cached_bank(bank_q),
        .captured_lanes(captured_q), .dirty_lanes(dirty_q),
        .cached_data(data_q),
        .requested_warp(requested_warp), .requested_reg(requested_reg),
        .requested_bank(requested_bank), .requested_lanes(requested_lanes),
        .forward_grant(raw_grant), .forwarded_data(raw_data)
    );

    wire live_write_hazard = write_hits_old
        && (|(requested_lanes & write_lanes));
    assign forward_grant = rst_n && !capture_en
        && raw_grant && !live_write_hazard
        && (!COVERAGE_GUARD || (coverage_ok && !coverage_fault));
    assign forwarded_data = forward_grant
        ? raw_data : {(LANES*DATA_BITS){1'b0}};
endmodule
