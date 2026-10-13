module vektor_wave32_full_frontend #(
 parameter LANES=32,REG_BITS=6,BANK_BITS=4,TAG_BITS=8
)(
 input wire clk,rst_n,enqueue_valid,output wire enqueue_ready,
 input wire [TAG_BITS-1:0] enqueue_tag,
 input wire [LANES-1:0] enqueue_mask,
 input wire [3*REG_BITS-1:0] enqueue_src_regs,
 input wire [1:0] rf_rsp_valid,
 input wire [2*REG_BITS-1:0] rf_rsp_reg,
 input wire [2*BANK_BITS-1:0] rf_rsp_bank,
 input wire [2*LANES*32-1:0] rf_rsp_data,
 output wire [1:0] rf_rsp_accept,
 input wire wb_valid,input wire [REG_BITS-1:0] wb_reg,
 input wire [LANES*32-1:0] wb_data,
 output wire out_valid,input wire out_ready,
 output wire [TAG_BITS-1:0] out_tag,
 output wire [LANES-1:0] out_mask,
 output wire [LANES*32-1:0] out_result,
 output wire [LANES*5-1:0] out_fflags
);
 wire mv,mr;wire [TAG_BITS-1:0] mt;
 wire [LANES-1:0] mm,ps,cs;
 wire [LANES*48-1:0] p;
 wire [LANES*11-1:0] pe,ce;
 wire [LANES*24-1:0] c;
 wire [LANES*9-1:0] cls;
 vektor_wave32_mul_frontend #(.LANES(LANES),.REG_BITS(REG_BITS),
  .BANK_BITS(BANK_BITS),.TAG_BITS(TAG_BITS)) mul_front(
  .clk(clk),.rst_n(rst_n),.enqueue_valid(enqueue_valid),
  .enqueue_ready(enqueue_ready),.enqueue_tag(enqueue_tag),
  .enqueue_mask(enqueue_mask),.enqueue_src_regs(enqueue_src_regs),
  .rf_rsp_valid(rf_rsp_valid),.rf_rsp_reg(rf_rsp_reg),
  .rf_rsp_bank(rf_rsp_bank),.rf_rsp_data(rf_rsp_data),
  .rf_rsp_accept(rf_rsp_accept),.wb_valid(wb_valid),.wb_reg(wb_reg),
  .wb_data(wb_data),.out_valid(mv),.out_ready(mr),
  .out_tag(mt),.out_mask(mm),.out_product(p),.out_product_exp(pe),
  .out_addend(c),.out_addend_exp(ce),.out_product_sign(ps),
  .out_addend_sign(cs),.out_classes(cls));
 vektor_wave32_full_slice #(.LANES(LANES),.TAG_BITS(TAG_BITS)) finisher(
  .clk(clk),.rst_n(rst_n),.in_valid(mv),.in_ready(mr),
  .in_tag(mt),.in_mask(mm),.in_product(p),.in_product_exp(pe),
  .in_addend(c),.in_addend_exp(ce),.in_product_sign(ps),
  .in_addend_sign(cs),.in_classes(cls),
  .out_valid(out_valid),.out_ready(out_ready),.out_tag(out_tag),
  .out_mask(out_mask),.out_result(out_result),.out_fflags(out_fflags));
endmodule
