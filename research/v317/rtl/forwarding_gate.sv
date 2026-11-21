// V317: freshness-safe lane-masked forwarding from an existing live buffer.
// The dirty bits MUST observe every intervening write to the physical
// warp/register and remain sticky until this cached value is replaced.
// No claim of novel GPU throughput or placed/routed timing is made.
module vektor_v317_forwarding_gate #(
    parameter integer WARP_BITS = 2,
    parameter integer REG_BITS = 4,
    parameter integer BANK_BITS = 2,
    parameter integer LANES = 4,
    parameter integer DATA_BITS = 8
) (
    input wire cached_valid,
    input wire [WARP_BITS-1:0] cached_warp,
    input wire [REG_BITS-1:0] cached_reg,
    input wire [BANK_BITS-1:0] cached_bank,
    input wire [LANES-1:0] captured_lanes,
    input wire [LANES-1:0] dirty_lanes,
    input wire [LANES*DATA_BITS-1:0] cached_data,
    input wire [WARP_BITS-1:0] requested_warp,
    input wire [REG_BITS-1:0] requested_reg,
    input wire [BANK_BITS-1:0] requested_bank,
    input wire [LANES-1:0] requested_lanes,
    output wire forward_grant,
    output wire [LANES*DATA_BITS-1:0] forwarded_data
);
    wire [LANES-1:0] missing = requested_lanes & ~captured_lanes;
    wire [LANES-1:0] stale = requested_lanes & dirty_lanes;
    assign forward_grant = cached_valid
        && (cached_warp == requested_warp)
        && (cached_reg == requested_reg)
        && (cached_bank == requested_bank)
        && (|requested_lanes)
        && !(|missing)
        && !(|stale);

    genvar lane;
    generate for (lane = 0; lane < LANES; lane = lane + 1) begin : lane_mux
        assign forwarded_data[lane*DATA_BITS +: DATA_BITS] =
            (forward_grant && requested_lanes[lane])
            ? cached_data[lane*DATA_BITS +: DATA_BITS] : {DATA_BITS{1'b0}};
    end endgenerate
endmodule
