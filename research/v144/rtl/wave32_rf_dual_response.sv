// V144: two physical Wave32 RF response vectors, one return per bank/cycle.
// Tags identify registers; multicast delivers one vector to all matching slots.
// This is a combinational RESPONSE ROUTER, not an RF, FMA or tile.
// Upstream must hold unaccepted responses and qualify by collector ID.
// src_regs/missing must remain stable while responses are outstanding.
module vektor_wave32_rf_dual_response #(
    parameter integer LANES=32,
    parameter integer REG_BITS=6,
    parameter integer BANK_BITS=4
)(
    input wire [3*REG_BITS-1:0] src_regs,
    input wire [2:0] missing,
    input wire [1:0] rf_rsp_valid,
    input wire [2*REG_BITS-1:0] rf_rsp_reg,
    input wire [2*BANK_BITS-1:0] rf_rsp_bank,
    input wire [2*LANES*32-1:0] rf_rsp_data,
    output wire [1:0] rf_rsp_accept,
    output wire [2:0] src_rsp_valid,
    output wire [3*LANES*32-1:0] src_rsp_data
);
    localparam integer WIDTH=LANES*32;
    wire bank_conflict=(rf_rsp_bank[0 +: BANK_BITS]==rf_rsp_bank[BANK_BITS +: BANK_BITS]);
    assign rf_rsp_accept[0]=rf_rsp_valid[0];
    assign rf_rsp_accept[1]=rf_rsp_valid[1] && !(rf_rsp_valid[0] && bank_conflict);
    genvar g;
    generate for (g=0;g<3;g=g+1) begin: SLOT
        wire hit0=rf_rsp_accept[0] &&
           (src_regs[g*REG_BITS +: REG_BITS]==rf_rsp_reg[0 +: REG_BITS]);
        wire hit1=rf_rsp_accept[1] &&
           (src_regs[g*REG_BITS +: REG_BITS]==rf_rsp_reg[REG_BITS +: REG_BITS]);
        assign src_rsp_valid[g]=missing[g] && (hit0 || hit1);
        // Zero on invalid is intentional; compare data only when valid.
        assign src_rsp_data[g*WIDTH +: WIDTH] =
            (missing[g] && hit1) ? rf_rsp_data[WIDTH +: WIDTH] :
            (missing[g] && hit0) ? rf_rsp_data[0 +: WIDTH] : {WIDTH{1'b0}};
    end endgenerate
endmodule
