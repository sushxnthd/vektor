module vektor_wave32_buffered_baseline #(parameter LANES=32,TAG_BITS=8)(
 input wire clk,rst_n,in_valid,output wire in_ready,
 input wire [TAG_BITS-1:0] in_tag,input wire [LANES-1:0] in_mask,
 input wire [LANES*48-1:0] in_product,
 input wire [LANES*11-1:0] in_product_exp,
 input wire [LANES*24-1:0] in_addend,
 input wire [LANES*11-1:0] in_addend_exp,
 input wire [LANES-1:0] in_product_sign,in_addend_sign,
 input wire [LANES*9-1:0] in_classes,
 output reg out_valid,input wire out_ready,
 output reg [TAG_BITS-1:0] out_tag,
 output reg [LANES-1:0] out_mask,
 output reg [LANES*32-1:0] out_result,
 output reg [LANES*5-1:0] out_fflags
);
 reg v1;
 reg [TAG_BITS-1:0] tag1;
 reg [LANES-1:0] mask1;
 reg [LANES*48-1:0] p1;
 reg [LANES*11-1:0] pe1;
 reg [LANES*24-1:0] a1;
 reg [LANES*11-1:0] ae1;
 reg [LANES-1:0] ps1,as1;
 reg [LANES*9-1:0] cls1;
 wire [LANES*32-1:0] result2;
 wire [LANES*5-1:0] flags2;
 wire ready2=(!out_valid)||out_ready;
 assign in_ready=rst_n&&((!v1)||ready2);
 genvar i;
 generate for(i=0;i<LANES;i=i+1) begin: lane
  vektor_fp32_bounded_tail fma(
   .product_sign(ps1[i]),.addend_sign(as1[i]),
   .product_exp(pe1[i*11+:11]),.addend_exp(ae1[i*11+:11]),
   .product(p1[i*48+:48]),.addend(a1[i*24+:24]),
   .classes(cls1[i*9+:9]),
   .result(result2[i*32+:32]),.fflags(flags2[i*5+:5]));
 end endgenerate
 always @(posedge clk or negedge rst_n) begin
  if(!rst_n) begin
   v1<=0;tag1<=0;mask1<=0;p1<=0;pe1<=0;a1<=0;ae1<=0;
   ps1<=0;as1<=0;cls1<=0;
   out_valid<=0;out_tag<=0;out_mask<=0;out_result<=0;out_fflags<=0;
  end else begin
   if(in_ready) begin
    v1<=in_valid;
    if(in_valid) begin
     tag1<=in_tag;mask1<=in_mask;
     p1<=in_product;pe1<=in_product_exp;
     a1<=in_addend;ae1<=in_addend_exp;
     ps1<=in_product_sign;as1<=in_addend_sign;cls1<=in_classes;
    end
   end
   if(ready2) begin
    out_valid<=v1;
    if(v1) begin
     out_tag<=tag1;out_mask<=mask1;
     out_result<=result2;out_fflags<=flags2;
    end
   end
  end
 end
endmodule
