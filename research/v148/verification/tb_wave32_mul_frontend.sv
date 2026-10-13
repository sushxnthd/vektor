`timescale 1ns/1ps
module tb_wave32_mul_frontend;
 localparam L=32,W=L*32;
 reg clk=0; always #5 clk=~clk;
 reg rst_n=0,enq=0,out_ready=0;
 reg [7:0] tag=0;
 reg [L-1:0] mask=0;
 reg [17:0] src=0;
 reg [1:0] rv=0;
 reg [11:0] rr=0;
 reg [7:0] rb=0;
 reg [2*W-1:0] rd=0;
 wire enq_ready,ov;
 wire [1:0] ra;
 wire [7:0] ot;
 wire [L-1:0] om,sp,sc;
 wire [L*48-1:0] product;
 wire [L*11-1:0] ep,ec;
 wire [L*24-1:0] addend;
 wire [L*9-1:0] classes;
 vektor_wave32_mul_frontend dut(
  .clk(clk),.rst_n(rst_n),.enqueue_valid(enq),.enqueue_ready(enq_ready),
  .enqueue_tag(tag),.enqueue_mask(mask),.enqueue_src_regs(src),
  .rf_rsp_valid(rv),.rf_rsp_reg(rr),.rf_rsp_bank(rb),
  .rf_rsp_data(rd),.rf_rsp_accept(ra),
  .wb_valid(1'b0),.wb_reg(6'b0),.wb_data({W{1'b0}}),
  .out_valid(ov),.out_ready(out_ready),.out_tag(ot),.out_mask(om),
  .out_product(product),.out_product_exp(ep),.out_addend(addend),
  .out_addend_exp(ec),.out_product_sign(sp),.out_addend_sign(sc),
  .out_classes(classes)
 );
 integer i,k;
 task check(input [7:0] expected_tag);
 begin
  if(ov!==1'b1 || ot!==expected_tag || om!==32'hf0f0f0f0)
   $fatal(1,"tag/mask/valid mismatch");
  for(k=0;k<L;k=k+1)
   if(product[k*48+:48]!==48'h600000000000 ||
      ep[k*11+:11]!==11'd2003 ||
      addend[k*24+:24]!==24'h800000 ||
      ec[k*11+:11]!==11'd2024 ||
      sp[k]!==0 || sc[k]!==0 || classes[k*9+:9]!==9'b001001001)
    $fatal(1,"lane %0d mismatch",k);
 end
 endtask
 task send(input [7:0] t);
 begin
  @(negedge clk);
  if(!enq_ready) $fatal(1,"enqueue not ready");
  enq=1;tag=t;mask=32'hf0f0f0f0;src={6'd33,6'd17,6'd1};
  @(negedge clk);enq=0;rv=2'b11;rr={6'd17,6'd1};rb={4'd1,4'd0};
  for(i=0;i<L;i=i+1) begin
   rd[i*32+:32]=32'h3fc00000;
   rd[W+i*32+:32]=32'h40000000;
  end
  #1;if(ra!==2'b11) $fatal(1,"first response pair rejected");
  @(negedge clk);rv=2'b01;rr={6'd0,6'd33};rb={4'd0,4'd2};
  for(i=0;i<L;i=i+1) rd[i*32+:32]=32'h3f000000;
  #1;if(ra!==2'b01) $fatal(1,"third response rejected");
  @(negedge clk);rv=0;
  repeat(3) @(negedge clk);
  check(t);
  repeat(4) begin @(negedge clk);check(t);end
  out_ready=1;
  @(negedge clk);out_ready=0;
  if(ov) $fatal(1,"output failed to retire");
 end
 endtask
 initial begin
  repeat(3) @(negedge clk);rst_n=1;
  send(8'h37);send(8'h91);
  $display("V148 PASS: 2 full-Wave32 collector->multiply transactions and output stalls");
  $finish;
 end
 initial begin #10000;$fatal(1,"timeout");end
endmodule
