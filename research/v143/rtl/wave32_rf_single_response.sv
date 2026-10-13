// One RF response vector per cycle. Qualify VALID, not 1024-bit data.
// Output data is unspecified for consumers whose src_rsp_valid is low.
// Different response-bandwidth topology from the 3-vector coalescer.
module vektor_wave32_rf_single_response #(
 parameter integer LANES=32, parameter integer REG_BITS=6
)(
 input wire [3*REG_BITS-1:0] src_regs,
 input wire [2:0] missing,
 input wire req_valid,
 output reg [2:0] rf_req,
 input wire rf_rsp_valid,
 input wire [REG_BITS-1:0] rf_rsp_reg,
 input wire [LANES*32-1:0] rf_rsp_data,
 output wire [2:0] src_rsp_valid,
 output wire [3*LANES*32-1:0] src_rsp_data
);
 integer i,j;
 reg duplicate;
 always @* begin
  rf_req=0;
  for(i=0;i<3;i=i+1) begin
   duplicate=0;
   for(j=0;j<i;j=j+1)
    if(missing[j] && src_regs[i*REG_BITS +: REG_BITS]==src_regs[j*REG_BITS +: REG_BITS])duplicate=1;
   if(req_valid && missing[i] && !duplicate)rf_req[i]=1;
  end
 end
 genvar g;
 generate for(g=0;g<3;g=g+1) begin: GEN
  assign src_rsp_valid[g]=missing[g] && rf_rsp_valid &&
     src_regs[g*REG_BITS +: REG_BITS]==rf_rsp_reg;
  assign src_rsp_data[g*LANES*32 +: LANES*32]=rf_rsp_data;
 end endgenerate
endmodule
