// V151 elastic Wave32 wrapper for the bounded RNE FP32 finisher.
// One result register, no architectural scoreboard or writeback.
module vektor_wave32_bounded_slice #(parameter LANES=32,TAG_BITS=8)(
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
 wire [LANES*32-1:0] res;
 wire [LANES*5-1:0] flags;
 genvar i;
 generate for(i=0;i<LANES;i=i+1) begin: LANE
  vektor_fp32_bounded_tail rounder(
   .product_sign(in_product_sign[i]),.addend_sign(in_addend_sign[i]),
   .product_exp(in_product_exp[i*11+:11]),
   .addend_exp(in_addend_exp[i*11+:11]),
   .product(in_product[i*48+:48]),
   .addend(in_addend[i*24+:24]),
   .classes(in_classes[i*9+:9]),
   .result(res[i*32+:32]),.fflags(flags[i*5+:5]));
 end endgenerate
 assign in_ready=rst_n&&(!out_valid||out_ready);
 always @(posedge clk or negedge rst_n) begin
  if(!rst_n) begin
   out_valid<=0;out_tag<=0;out_mask<=0;out_result<=0;out_fflags<=0;
  end else if(in_ready) begin
   out_valid<=in_valid;
   if(in_valid) begin
    out_tag<=in_tag;out_mask<=in_mask;
    out_result<=res;out_fflags<=flags;
   end
  end
 end
endmodule
