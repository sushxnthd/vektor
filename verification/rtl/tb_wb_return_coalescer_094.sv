`timescale 1ns/1ps
module tb_wb_return_coalescer_094;
 reg clk=0;always #5 clk=~clk;
 reg rst_n=0,req_valid=0,source_beat_valid=0,ret_ready=0;
 reg [1:0] req_tag=0;
 reg [2:0] expected_beats=0;
 wire req_ready,ret_valid,ret_final;
 wire [1:0] ret_tag;
 wb_return_coalescer_094 #(.TAG_BITS(2),.COUNT_BITS(3)) dut(
  .clk(clk),.rst_n(rst_n),.req_valid(req_valid),.req_ready(req_ready),
  .req_tag(req_tag),.expected_beats(expected_beats),
  .source_beat_valid(source_beat_valid),.ret_valid(ret_valid),
  .ret_ready(ret_ready),.ret_tag(ret_tag),.ret_final(ret_final));
 initial begin
  repeat(2)@(negedge clk);
  rst_n=1;req_valid=1;req_tag=2;expected_beats=3;
  @(posedge clk);#1;req_valid=0;
  repeat(2)begin
   @(negedge clk);source_beat_valid=1;
   @(posedge clk);#1;
   if(ret_valid)$fatal(1,"early");
  end
  @(negedge clk);source_beat_valid=1;
  @(posedge clk);#1;
  if(!ret_valid||!ret_final||ret_tag!=2)$fatal(1,"missing final");
  @(negedge clk);source_beat_valid=0;
  repeat(3)begin
   @(posedge clk);#1;
   if(!ret_valid||!ret_final)$fatal(1,"held");
  end
  @(negedge clk);ret_ready=1;
  @(posedge clk);#1;
  if(ret_valid||!req_ready)$fatal(1,"consume");
  $display("PASS coalescer");$finish;
 end
endmodule
