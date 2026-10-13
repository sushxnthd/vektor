// V148: elastic tagged Wave32 multiplier stage, NOT complete IEEE FMA.
module vektor_wave32_mul_slice #(parameter LANES=32, TAG_BITS=8)(
 input wire clk,rst_n,in_valid, output wire in_ready,
 input wire [TAG_BITS-1:0] in_tag,
 input wire [LANES-1:0] in_mask,
 input wire [3*LANES*32-1:0] in_operands,
 output reg out_valid,input wire out_ready,
 output reg [TAG_BITS-1:0] out_tag,
 output reg [LANES-1:0] out_mask,
 output reg [LANES*48-1:0] out_product,
 output reg [LANES*11-1:0] out_product_exp,
 output reg [LANES*24-1:0] out_addend,
 output reg [LANES*11-1:0] out_addend_exp,
 output reg [LANES-1:0] out_product_sign,out_addend_sign,
 output reg [LANES*9-1:0] out_classes
);
 wire [LANES*48-1:0] p;
 wire [LANES*11-1:0] ep,ec;
 wire [LANES*24-1:0] sc;
 wire [LANES-1:0] sp,scc;
 wire [LANES*9-1:0] cls;
 genvar i;
 generate for(i=0;i<LANES;i=i+1) begin: LANE
   vektor_fp32_mul_lane u(
    .a(in_operands[i*32+:32]),
    .b(in_operands[(LANES+i)*32+:32]),
    .c(in_operands[(2*LANES+i)*32+:32]),
    .product(p[i*48+:48]),.product_exp(ep[i*11+:11]),
    .addend(sc[i*24+:24]),.addend_exp(ec[i*11+:11]),
    .product_sign(sp[i]),.addend_sign(scc[i]),
    .classes(cls[i*9+:9])
   );
 end endgenerate
 assign in_ready=rst_n && (!out_valid || out_ready);
 always @(posedge clk or negedge rst_n) begin
  if(!rst_n) begin
   out_valid<=0;out_tag<=0;out_mask<=0;
   out_product<=0;out_product_exp<=0;out_addend<=0;
   out_addend_exp<=0;out_product_sign<=0;out_addend_sign<=0;
   out_classes<=0;
  end else if(in_ready) begin
   out_valid<=in_valid;
   if(in_valid) begin
    out_tag<=in_tag;out_mask<=in_mask;
    out_product<=p;out_product_exp<=ep;
    out_addend<=sc;out_addend_exp<=ec;
    out_product_sign<=sp;out_addend_sign<=scc;
    out_classes<=cls;
   end
  end
 end
endmodule
