`timescale 1ns/1ps
module tb_wb_return_packetizer_094;
 reg clk=0; always #5 clk=~clk;
 reg rst_n=0,req_valid=0,ret_ready=0;
 reg [1:0] req_tag=0;
 reg [2:0] req_copies=0;
 wire req_ready,ret_valid,ret_final;
 wire [1:0] ret_tag;
 integer beats=0,finals=0;
 wb_return_packetizer_094 #(.TAG_BITS(2),.COPIES_BITS(3)) dut(
  .clk(clk),.rst_n(rst_n),.req_valid(req_valid),.req_ready(req_ready),
  .req_tag(req_tag),.req_copies(req_copies),.ret_valid(ret_valid),
  .ret_ready(ret_ready),.ret_tag(ret_tag),.ret_final(ret_final));
 initial begin
  repeat(2) @(negedge clk);
  rst_n=1;req_valid=1;req_tag=2;req_copies=3;
  @(posedge clk);#1;req_valid=0;
  if(!ret_valid||ret_tag!=2||ret_final)$fatal(1,"initial");
  repeat(2) begin
   @(negedge clk);ret_ready=0;
   @(posedge clk);#1;
   if(!ret_valid||ret_final)$fatal(1,"backpressure");
  end
  repeat(3) begin
   @(negedge clk);ret_ready=1;
   if(!ret_valid||ret_tag!=2)$fatal(1,"beat");
   if(ret_final!=(beats==2))$fatal(1,"final");
   beats=beats+1;
   if(ret_final)finals=finals+1;
   @(posedge clk);#1;
  end
  if(beats!=3||finals!=1||ret_valid||!req_ready)$fatal(1,"count");
  $display("PASS packetizer");$finish;
 end
endmodule
