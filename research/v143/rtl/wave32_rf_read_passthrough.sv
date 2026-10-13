// Identical 3-source logical response interface, no duplicate-read coalescing.
module vektor_wave32_rf_read_passthrough #(
 parameter integer LANES=32, parameter integer REG_BITS=6
)(
 input wire [3*REG_BITS-1:0] src_regs,
 input wire [2:0] missing,
 input wire req_valid,
 output wire [2:0] rf_req,
 input wire [2:0] rf_rsp_valid,
 input wire [3*LANES*32-1:0] rf_rsp_data,
 output wire [2:0] src_rsp_valid,
 output wire [3*LANES*32-1:0] src_rsp_data
);
 assign rf_req={3{req_valid}} & missing;
 assign src_rsp_valid=rf_rsp_valid & missing;
 assign src_rsp_data=rf_rsp_data;
endmodule
