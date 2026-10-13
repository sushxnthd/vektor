// V146 Wave32 operand collector. One instruction in flight.
// Upstream must hold RF responses until rf_rsp_accept; response tags stable.
module vektor_wave32_operand_collector #(
 parameter LANES=32, REG_BITS=6, BANK_BITS=4, TAG_BITS=8
)(
 input wire clk,rst_n,
 input wire enqueue_valid, output wire enqueue_ready,
 input wire [TAG_BITS-1:0] enqueue_tag,
 input wire [3*REG_BITS-1:0] enqueue_src_regs,
 input wire [1:0] rf_rsp_valid,
 input wire [2*REG_BITS-1:0] rf_rsp_reg,
 input wire [2*BANK_BITS-1:0] rf_rsp_bank,
 input wire [2*LANES*32-1:0] rf_rsp_data,
 output wire [1:0] rf_rsp_accept,
 input wire wb_valid, input wire [REG_BITS-1:0] wb_reg,
 input wire [LANES*32-1:0] wb_data,
 output wire dispatch_valid, input wire dispatch_ready,
 output wire [TAG_BITS-1:0] dispatch_tag,
 output wire [3*LANES*32-1:0] dispatch_operands,
 output wire [2:0] captured_debug
);
 localparam WIDTH=LANES*32;
 reg active;
 reg [TAG_BITS-1:0] tag_q;
 reg [3*REG_BITS-1:0] src_q;
 reg [2:0] captured_q;
 reg [3*WIDTH-1:0] operand_q;
 wire [2:0] pending={3{active}} & ~captured_q;
 wire [1:0] eligible;
 wire [2:0] src_rsp_valid;
 wire [3*WIDTH-1:0] src_rsp_data;
 assign enqueue_ready=!active && rst_n;
 assign dispatch_valid=active && (&captured_q) && rst_n;
 assign dispatch_tag=tag_q;
 assign dispatch_operands=operand_q;
 assign captured_debug=captured_q;
 genvar p;
 generate for(p=0;p<2;p=p+1) begin: ELIG
   wire [REG_BITS-1:0] candidate=rf_rsp_reg[p*REG_BITS +: REG_BITS];
   wire [2:0] hits;
   genvar s;
   for(s=0;s<3;s=s+1) begin: SLOT
     assign hits[s]=pending[s] && src_q[s*REG_BITS +: REG_BITS]==candidate;
   end
   assign eligible[p]=rf_rsp_valid[p] && (|hits) &&
                      !(wb_valid && wb_reg==candidate);
 end endgenerate
 vektor_wave32_rf_dual_response #(
  .LANES(LANES),.REG_BITS(REG_BITS),.BANK_BITS(BANK_BITS)
 ) router (
  .src_regs(src_q),.missing(pending),.rf_rsp_valid(eligible),
  .rf_rsp_reg(rf_rsp_reg),.rf_rsp_bank(rf_rsp_bank),
  .rf_rsp_data(rf_rsp_data),.rf_rsp_accept(rf_rsp_accept),
  .src_rsp_valid(src_rsp_valid),.src_rsp_data(src_rsp_data)
 );
 integer j;
 always @(posedge clk or negedge rst_n) begin
  if(!rst_n) begin
   active<=0; tag_q<=0; src_q<=0; captured_q<=0; operand_q<=0;
  end else if(!active) begin
   if(enqueue_valid) begin
    active<=1; tag_q<=enqueue_tag; src_q<=enqueue_src_regs;
    captured_q<=0; operand_q<=0;
   end
  end else if(dispatch_valid && dispatch_ready) begin
   active<=0; captured_q<=0;
  end else begin
   for(j=0;j<3;j=j+1) if(!captured_q[j]) begin
    if(wb_valid && wb_reg==src_q[j*REG_BITS +: REG_BITS]) begin
     captured_q[j]<=1;
     operand_q[j*WIDTH +: WIDTH]<=wb_data;
    end else if(src_rsp_valid[j]) begin
     captured_q[j]<=1;
     operand_q[j*WIDTH +: WIDTH]<=src_rsp_data[j*WIDTH +: WIDTH];
    end
   end
  end
 end
endmodule
