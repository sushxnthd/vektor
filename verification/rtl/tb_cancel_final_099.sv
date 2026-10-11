`timescale 1ns/1ps
module tb_cancel_final_099;
  localparam TAG_BITS=2,N=4;
  reg clk=0;
  always #5 clk=~clk;
  reg rst_n=0,soft_reset=0,flush_ack=0,offer=0,cb_valid=0,cb_final=0;
  reg [N-1:0] cancel_mask=0;
  reg [TAG_BITS-1:0] cb_tag=0;
  wire grant_old,grant_new,complete_old,complete_new,stale_old,stale_new;
  wire ignored_old,ignored_new,stall_old,stall_new,ready_old,ready_new;
  wire [TAG_BITS-1:0] tag_old,tag_new;
  wire [N-1:0] pending_old,pending_new,live_old,live_new;
  integer scenarios=0;
  wb_final_consumer_094 #(.TAG_BITS(TAG_BITS)) old_dut (
    .clk(clk),.cold_rst_n(rst_n),.soft_reset(soft_reset),.flush_ack(flush_ack),
    .offer(offer),.cancel_mask(cancel_mask),.cb_valid(cb_valid),
    .cb_final(cb_final),.cb_tag(cb_tag),.grant(grant_old),
    .grant_tag(tag_old),.complete(complete_old),.stale_drop(stale_old),
    .nonfinal_ignored(ignored_old),.tag_stall(stall_old),.ready(ready_old),
    .pending_mask(pending_old),.live_mask(live_old));
  wb_final_consumer_099 #(.TAG_BITS(TAG_BITS)) new_dut (
    .clk(clk),.cold_rst_n(rst_n),.soft_reset(soft_reset),.flush_ack(flush_ack),
    .offer(offer),.cancel_mask(cancel_mask),.cb_valid(cb_valid),
    .cb_final(cb_final),.cb_tag(cb_tag),.grant(grant_new),
    .grant_tag(tag_new),.complete(complete_new),.stale_drop(stale_new),
    .nonfinal_ignored(ignored_new),.tag_stall(stall_new),.ready(ready_new),
    .pending_mask(pending_new),.live_mask(live_new));
  task reset_and_admit;
    begin
      @(negedge clk); rst_n=0;flush_ack=0;offer=0;soft_reset=0;
      cancel_mask=0;cb_valid=0;cb_final=0;cb_tag=0;
      repeat(2) @(negedge clk);
      rst_n=1;flush_ack=1;
      @(negedge clk);flush_ack=0;offer=1;
      @(posedge clk);#1;
      if(!grant_old || !grant_new || tag_old !== tag_new)
        $fatal(1,"admission failed");
      cb_tag=tag_old;
      @(negedge clk);offer=0;
      if(!pending_old[cb_tag] || !pending_new[cb_tag])
        $fatal(1,"pending missing");
    end
  endtask
  task retire_and_check;
    input reg cancel_now;
    input reg soft_now;
    input reg final_now;
    input reg expect_old;
    input reg expect_new;
    begin
      cancel_mask=cancel_now ? ({{(N-1){1'b0}},1'b1} << cb_tag) : 0;
      soft_reset=soft_now;
      cb_valid=1;cb_final=final_now;
      @(posedge clk);#1;
      if(complete_old !== expect_old || complete_new !== expect_new)
        $fatal(1,"completion mismatch scenario=%0d old=%b new=%b",scenarios,complete_old,complete_new);
      if(final_now && (pending_old !== pending_new || pending_new !== 0))
        $fatal(1,"pending conservation failed");
      if(final_now && (stale_new !== !expect_new))
        $fatal(1,"stale classification mismatch");
      scenarios=scenarios+1;
    end
  endtask
  initial begin
    reset_and_admit();
    retire_and_check(1,0,1,1,0); // V094 FINAL-wins; V099 cancel-wins
    reset_and_admit();
    retire_and_check(0,0,1,1,1);
    reset_and_admit();
    retire_and_check(0,1,1,0,0);
    reset_and_admit();
    retire_and_check(1,0,0,0,0);
    if(pending_new==0)$fatal(1,"nonfinal incorrectly retired");
    @(negedge clk);cb_valid=1;cb_final=1;cancel_mask=0;
    @(posedge clk);#1;
    if(complete_new || !stale_new)$fatal(1,"cancelled tag unexpectedly completed");
    scenarios=scenarios+1;
    $display("PASS V099 cancel-wins race: %0d directed checks",scenarios);
    $finish;
  end
endmodule
