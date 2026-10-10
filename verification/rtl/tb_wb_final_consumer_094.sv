`timescale 1ns/1ps
module tb_wb_final_consumer_094;
 reg clk=0;always #5 clk=~clk;
 reg cold_rst_n=0,soft_reset=0,flush_ack=0,offer=0,cb_valid=0,cb_final=0;
 reg [1:0] cb_tag=0;
 reg [3:0] cancel_mask=0;
 wire grant,complete,stale_drop,nonfinal_ignored,tag_stall,ready;
 wire [1:0] grant_tag;
 wire [3:0] pending_mask,live_mask;
 wb_final_consumer_094 #(.TAG_BITS(2),.N(4)) dut(
  .clk(clk),.cold_rst_n(cold_rst_n),.soft_reset(soft_reset),
  .flush_ack(flush_ack),.offer(offer),.cancel_mask(cancel_mask),
  .cb_valid(cb_valid),.cb_final(cb_final),.cb_tag(cb_tag),
  .grant(grant),.grant_tag(grant_tag),.complete(complete),
  .stale_drop(stale_drop),.nonfinal_ignored(nonfinal_ignored),
  .tag_stall(tag_stall),.ready(ready),.pending_mask(pending_mask),.live_mask(live_mask));
 initial begin
  repeat(2)@(negedge clk);
  cold_rst_n=1;flush_ack=1;
  @(posedge clk);#1;
  @(negedge clk);flush_ack=0;offer=1;
  @(posedge clk);#1;
  if(!grant||grant_tag!=0||!pending_mask[0])$fatal(1,"grant");
  @(negedge clk);offer=0;cb_valid=1;cb_final=0;cb_tag=0;
  @(posedge clk);#1;
  if(!pending_mask[0]||complete||!nonfinal_ignored)$fatal(1,"nonfinal");
  @(negedge clk);cb_final=1;
  @(posedge clk);#1;
  if(pending_mask[0]||!complete)$fatal(1,"final");
  @(negedge clk);cb_valid=0;offer=1;
  @(posedge clk);#1;
  if(!grant||grant_tag!=1)$fatal(1,"second grant");
  @(negedge clk);offer=0;soft_reset=1;
  @(posedge clk);#1;
  if(!pending_mask[1]||live_mask[1])$fatal(1,"reset");
  @(negedge clk);soft_reset=0;cb_valid=1;cb_final=1;cb_tag=1;
  @(posedge clk);#1;
  if(complete||!stale_drop||pending_mask[1])$fatal(1,"stale");
  $display("PASS consumer");$finish;
 end
endmodule
