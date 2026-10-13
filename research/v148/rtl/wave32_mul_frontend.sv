// V148: registered collector -> tagged FP32 significand multiplier.
// No scoreboard, rounded FMA, or architectural writeback yet.
module vektor_wave32_mul_frontend #(
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
 output wire [LANES*48-1:0] out_product,
 output wire [LANES*11-1:0] out_product_exp,
 output wire [LANES*24-1:0] out_addend,
 output wire [LANES*11-1:0] out_addend_exp,
 output wire [LANES-1:0] out_product_sign,out_addend_sign,
 output wire [LANES*9-1:0] out_classes
);
 wire dv,dr;
 wire [TAG_BITS-1:0] dt;
 wire [3*LANES*32-1:0] operands;
 reg [LANES-1:0] mask_q;
 always @(posedge clk or negedge rst_n)
  if(!rst_n) mask_q<=0;
  else if(enqueue_valid && enqueue_ready) mask_q<=enqueue_mask;
 vektor_wave32_operand_collector #(
  .LANES(LANES),.REG_BITS(REG_BITS),.BANK_BITS(BANK_BITS),.TAG_BITS(TAG_BITS)
 ) collector(
  .clk(clk),.rst_n(rst_n),.enqueue_valid(enqueue_valid),
  .enqueue_ready(enqueue_ready),.enqueue_tag(enqueue_tag),
  .enqueue_src_regs(enqueue_src_regs),.rf_rsp_valid(rf_rsp_valid),
  .rf_rsp_reg(rf_rsp_reg),.rf_rsp_bank(rf_rsp_bank),
  .rf_rsp_data(rf_rsp_data),.rf_rsp_accept(rf_rsp_accept),
  .wb_valid(wb_valid),.wb_reg(wb_reg),.wb_data(wb_data),
  .dispatch_valid(dv),.dispatch_ready(dr),.dispatch_tag(dt),
  .dispatch_operands(operands),.captured_debug()
 );
 vektor_wave32_mul_slice #(.LANES(LANES),.TAG_BITS(TAG_BITS)) mul(
  .clk(clk),.rst_n(rst_n),.in_valid(dv),.in_ready(dr),
  .in_tag(dt),.in_mask(mask_q),.in_operands(operands),
  .out_valid(out_valid),.out_ready(out_ready),
  .out_tag(out_tag),.out_mask(out_mask),
  .out_product(out_product),.out_product_exp(out_product_exp),
  .out_addend(out_addend),.out_addend_exp(out_addend_exp),
  .out_product_sign(out_product_sign),
  .out_addend_sign(out_addend_sign),.out_classes(out_classes)
 );
endmodule
