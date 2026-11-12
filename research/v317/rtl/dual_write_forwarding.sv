// V317 dual-physical-write-source correctness instrument.
// A complete, coherent write-event stream from BOTH physical ports is required.
// This is not a proposed GPU throughput optimization.
module vektor_v317_dual_write_forwarding #(
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
    input wire write0_en,
    input wire [WARP_BITS-1:0] write0_warp,
    input wire [REG_BITS-1:0] write0_reg,
    input wire [BANK_BITS-1:0] write0_bank,
    input wire [LANES-1:0] write0_lanes,
    input wire write1_en,
    input wire [WARP_BITS-1:0] write1_warp,
    input wire [REG_BITS-1:0] write1_reg,
    input wire [BANK_BITS-1:0] write1_bank,
    input wire [LANES-1:0] write1_lanes,
    input wire [WARP_BITS-1:0] requested_warp,
    input wire [REG_BITS-1:0] requested_reg,
    input wire [BANK_BITS-1:0] requested_bank,
    input wire [LANES-1:0] requested_lanes,
    output wire forward_grant,
    output wire [LANES*DATA_BITS-1:0] forwarded_data
);
    reg valid_q;
    reg coverage_fault_q;
    reg [WARP_BITS-1:0] warp_q;
    reg [REG_BITS-1:0] reg_q;
    reg [BANK_BITS-1:0] bank_q;
    reg [LANES-1:0] captured_q, dirty_q;
    reg [LANES*DATA_BITS-1:0] data_q;

    wire old0 = write0_en && valid_q &&
        write0_warp == warp_q && write0_reg == reg_q &&
        write0_bank == bank_q;
    wire old1 = write1_en && valid_q &&
        write1_warp == warp_q && write1_reg == reg_q &&
        write1_bank == bank_q;
    wire cap0 = write0_en &&
        write0_warp == capture_warp && write0_reg == capture_reg &&
        write0_bank == capture_bank;
    wire cap1 = write1_en &&
        write1_warp == capture_warp && write1_reg == capture_reg &&
        write1_bank == capture_bank;
    wire [LANES-1:0] old_dirty =
        (old0 ? write0_lanes : {LANES{1'b0}}) |
        (old1 ? write1_lanes : {LANES{1'b0}});
    wire [LANES-1:0] cap_dirty =
        (cap0 ? write0_lanes : {LANES{1'b0}}) |
        (cap1 ? write1_lanes : {LANES{1'b0}});

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            valid_q <= 1'b0;
            coverage_fault_q <= 1'b1;
            warp_q <= {WARP_BITS{1'b0}};
            reg_q <= {REG_BITS{1'b0}};
            bank_q <= {BANK_BITS{1'b0}};
            captured_q <= {LANES{1'b0}};
            dirty_q <= {LANES{1'b0}};
            data_q <= {(LANES*DATA_BITS){1'b0}};
        end else begin
            if (capture_en) begin
                valid_q <= 1'b1;
                warp_q <= capture_warp;
                reg_q <= capture_reg;
                bank_q <= capture_bank;
                captured_q <= capture_lanes;
                data_q <= capture_data;
                // Capture/write ordering is unspecified: dirty both overlaps.
                dirty_q <= capture_lanes & cap_dirty;
                // Only a coherent capture under complete coverage clears fault.
                coverage_fault_q <= !coverage_ok;
            end else begin
                dirty_q <= dirty_q | old_dirty;
                if (!coverage_ok)
                    coverage_fault_q <= 1'b1;
            end
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

    wire live_hazard = |(requested_lanes & old_dirty);
    assign forward_grant = rst_n && !capture_en && coverage_ok &&
        !coverage_fault_q && raw_grant && !live_hazard;
    assign forwarded_data = forward_grant ? raw_data :
        {(LANES*DATA_BITS){1'b0}};
endmodule
