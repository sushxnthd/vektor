// V153 two elastic stages: signed accumulation -> register -> RNE pack -> register.
// Functional architecture candidate; not yet an IEEE-754 complete GPU tile.
module vektor_wave32_cutset_pipe #(parameter LANES=32,TAG_BITS=8,W=64)(
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
 wire [LANES*(W+1)-1:0] pm;
 wire [LANES-1:0] ps,pt,po,pb;
 wire [LANES*32-1:0] pl,pr;
 wire [LANES*5-1:0] pf;
 reg v1;
 reg [TAG_BITS-1:0] tag1;
 reg [LANES-1:0] mask1;
 reg [LANES*(W+1)-1:0] m1;
 reg [LANES-1:0] s1,t1,o1,b1;
 reg [LANES*32-1:0] l1,r1;
 reg [LANES*5-1:0] f1;
 wire [LANES*32-1:0] r2;
 wire [LANES*5-1:0] f2;
 wire ready2=(!out_valid)||out_ready;
 assign in_ready=rst_n&&((!v1)||ready2);
 genvar i;
 generate for(i=0;i<LANES;i=i+1) begin: lane
  vektor_fp32_bounded_prepare #(.W(W)) pre(
   .product_sign(in_product_sign[i]),.addend_sign(in_addend_sign[i]),
   .product_exp(in_product_exp[i*11+:11]),.addend_exp(in_addend_exp[i*11+:11]),
   .product(in_product[i*48+:48]),.addend(in_addend[i*24+:24]),
   .classes(in_classes[i*9+:9]),.mag_o(pm[i*(W+1)+:(W+1)]),
   .sign_o(ps[i]),.lowest_exp_o(pl[i*32+:32]),
   .tail_present_o(pt[i]),.tail_opposes_o(po[i]),.bypass_o(pb[i]),
   .result(pr[i*32+:32]),.fflags(pf[i*5+:5]));
  vektor_fp32_bounded_finish #(.W(W)) post(
   .mag(m1[i*(W+1)+:(W+1)]),.sign(s1[i]),
   .lowest_exp(l1[i*32+:32]),.tail_present(t1[i]),
   .tail_opposes(o1[i]),.bypass(b1[i]),
   .bypass_result(r1[i*32+:32]),.bypass_fflags(f1[i*5+:5]),
   .result(r2[i*32+:32]),.fflags(f2[i*5+:5]));
 end endgenerate
 always @(posedge clk or negedge rst_n) begin
  if(!rst_n) begin
   v1<=0;tag1<=0;mask1<=0;m1<=0;s1<=0;t1<=0;o1<=0;b1<=0;
   l1<=0;r1<=0;f1<=0;
   out_valid<=0;out_tag<=0;out_mask<=0;out_result<=0;out_fflags<=0;
  end else begin
   if(in_ready) begin
    v1<=in_valid;
    if(in_valid) begin
     tag1<=in_tag;mask1<=in_mask;m1<=pm;s1<=ps;t1<=pt;o1<=po;
     b1<=pb;l1<=pl;r1<=pr;f1<=pf;
    end
   end
   if(ready2) begin
    out_valid<=v1;
    if(v1) begin
     out_tag<=tag1;out_mask<=mask1;out_result<=r2;out_fflags<=f2;
    end
   end
  end
 end
endmodule
