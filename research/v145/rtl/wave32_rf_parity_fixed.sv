// V145: two 1024-bit response ports physically partitioned by bank parity.
// Port 0 serves even banks, port 1 odd banks; bank(reg)=reg_id % 16.
// This is a response router, NOT an RF, collector, FMA or complete V-Tile.
// Upstream must retain unaccepted responses and qualify collector identity.
module vektor_wave32_rf_parity_fixed #(
 parameter integer LANES=32, REG_BITS=6, BANK_BITS=4
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
 wire even_ok=(rf_rsp_bank[0 +: BANK_BITS]==rf_rsp_reg[0 +: BANK_BITS]) && !rf_rsp_bank[0];
 wire odd_ok=(rf_rsp_bank[BANK_BITS +: BANK_BITS]==rf_rsp_reg[REG_BITS +: BANK_BITS]) && rf_rsp_bank[BANK_BITS];
 assign rf_rsp_accept[0]=rf_rsp_valid[0] && even_ok;
 assign rf_rsp_accept[1]=rf_rsp_valid[1] && odd_ok;
 genvar g;
 generate for(g=0;g<3;g=g+1)begin:SLOT
   wire odd=src_regs[g*REG_BITS];
   wire hit_even=rf_rsp_accept[0] && !odd &&
       (src_regs[g*REG_BITS +: REG_BITS]==rf_rsp_reg[0 +: REG_BITS]);
   wire hit_odd=rf_rsp_accept[1] && odd &&
       (src_regs[g*REG_BITS +: REG_BITS]==rf_rsp_reg[REG_BITS +: REG_BITS]);
   assign src_rsp_valid[g]=missing[g] && (hit_even || hit_odd);
   wire [WIDTH-1:0] selected=odd ? rf_rsp_data[WIDTH +: WIDTH] : rf_rsp_data[0 +: WIDTH];
   assign src_rsp_data[g*WIDTH +: WIDTH]=src_rsp_valid[g] ? selected : {WIDTH{1'b0}};
 end endgenerate
endmodule
