`timescale 1ns/1ps
// V101 composed differential test. V098 is a deliberate policy negative control.
// Observations after the edge correspond to decisions made before that edge.
module tb_wb_multisource_101;
 parameter integer SOURCES=4,TAG_BITS=3,DEPTH=4,COPIES=3,GUARD=8;
 localparam integer N=(1<<TAG_BITS), IDX_BITS=$clog2(SOURCES),PTR_BITS=$clog2(DEPTH);
 reg clk=0; always #5 clk=~clk;
 reg cold_rst_n=0,soft_reset=0,flush_ack=0,offer=0,fabric_hold=0;
 reg race_enable=0;
 wire [N-1:0] cancel_mask;
 wire complete_new,stale_new,tag_stall_new,grant_new,launch_new,fire_new,final_new;
 wire complete_old,stale_old,tag_stall_old,grant_old,launch_old,fire_old,final_old;
 wire [TAG_BITS-1:0] tag_new,tag_old;
 wire [IDX_BITS-1:0] src_new,src_old;
 wire [N-1:0] pending_new,pending_old;
 wire [PTR_BITS:0] launch_occ_new,launch_occ_old;
 wire [SOURCES*(PTR_BITS+1)-1:0] ret_occ_new,ret_occ_old;
 integer t,grants=0,finals=0,races=0,beats=0,completions_new=0,stales_new=0;
 integer old_completions=0, stalls=0, immediate_reuses=0;
 reg expected_race;
 reg stalled=0;
 reg [TAG_BITS-1:0] stalled_tag;
 reg [IDX_BITS-1:0] stalled_source;
 reg stalled_final;
 assign cancel_mask=(race_enable && fire_new && final_new) ? ({{(N-1){1'b0}},1'b1} << tag_new) : {N{1'b0}};
 wb_multisource_composed_100 #(.TAG_BITS(TAG_BITS),.DEPTH(DEPTH),.SOURCES(SOURCES),.COPIES(COPIES),.GUARD(GUARD)) dut (
  .clk(clk),.cold_rst_n(cold_rst_n),.soft_reset(soft_reset),.flush_ack(flush_ack),.offer(offer),.fabric_hold(fabric_hold),.cancel_mask(cancel_mask),
  .complete(complete_new),.stale_drop(stale_new),.tag_stall(tag_stall_new),.grant_pulse(grant_new),.launch_fire(launch_new),.return_fire(fire_new),
  .return_final(final_new),.return_tag(tag_new),.return_source(src_new),.pending_mask(pending_new),.launch_occupancy(launch_occ_new),.return_occupancies(ret_occ_new));
 wb_multisource_composed_098 #(.TAG_BITS(TAG_BITS),.DEPTH(DEPTH),.SOURCES(SOURCES),.COPIES(COPIES),.GUARD(GUARD)) negative_control (
  .clk(clk),.cold_rst_n(cold_rst_n),.soft_reset(soft_reset),.flush_ack(flush_ack),.offer(offer),.fabric_hold(fabric_hold),.cancel_mask(cancel_mask),
  .complete(complete_old),.stale_drop(stale_old),.tag_stall(tag_stall_old),.grant_pulse(grant_old),.launch_fire(launch_old),.return_fire(fire_old),
  .return_final(final_old),.return_tag(tag_old),.return_source(src_old),.pending_mask(pending_old),.launch_occupancy(launch_occ_old),.return_occupancies(ret_occ_old));
 always @(posedge clk) if(cold_rst_n) begin
  expected_race=fire_new && final_new && race_enable && dut.live_mask[tag_new] && pending_new[tag_new] && !soft_reset;
  if(stalled && (!dut.arb_valid || tag_new !== stalled_tag || src_new !== stalled_source || final_new !== stalled_final))
   $fatal(1,"stall-stability violation");
  stalled=dut.arb_valid && fabric_hold;
  if(stalled)stalls=stalls+1;
  stalled_tag=tag_new;stalled_source=src_new;stalled_final=final_new;
  if(grant_new)grants=grants+1;
  if(fire_new)begin beats=beats+1; if(final_new)finals=finals+1; end
  if(complete_new)completions_new=completions_new+1;
  if(stale_new)stales_new=stales_new+1;
  if(complete_old)old_completions=old_completions+1;
  #1;
  if(pending_new !== pending_old || dut.live_mask !== negative_control.live_mask)
   $fatal(1,"consumer state divergence");
  if(grant_new !== grant_old || fire_new !== fire_old || tag_new !== tag_old || src_new !== src_old)
   $fatal(1,"fabric handshake divergence");
  if(expected_race)begin
   races=races+1;
   if(complete_new !== 0 || stale_new !== 1 || complete_old !== 1 || stale_old !== 0)
    $fatal(1,"cancel-wins classification mismatch");
   if(grant_new && dut.grant_tag==tag_new)immediate_reuses=immediate_reuses+1;
  end
 end
 initial begin
  repeat(4) @(negedge clk);
  cold_rst_n=1;flush_ack=1;
  for(t=0;t<3600;t=t+1)begin
   @(negedge clk);
   offer=(t<3200)&&((t%17)<15);
   fabric_hold=((t%67)<29)||((t%131)>120);
   soft_reset=(t==270 || t==710 || t==1500);
   race_enable=(t>=800 && t<1300) || (t>=1900 && t<2600);
  end
  @(negedge clk);offer=0;soft_reset=0;race_enable=0;fabric_hold=0;
  repeat(700) @(negedge clk);
  #2;
  if(pending_new!==0 || pending_old!==0 || launch_occ_new!==0 || ret_occ_new!==0)
   $fatal(1,"drain failed");
  if(grants!=finals || finals!=completions_new+stales_new)
   $fatal(1,"conservation failure grants=%0d finals=%0d completed=%0d stale=%0d",grants,finals,completions_new,stales_new);
  if(races<5)$fatal(1,"insufficient cancel/FINAL race coverage %0d",races);
  if(old_completions-completions_new!=races)
   $fatal(1,"race residual=%0d",old_completions-completions_new-races);
  if(beats!=COPIES*finals)$fatal(1,"beat conservation failed");
  if(stalls<10)$fatal(1,"insufficient stall coverage");
  $display("PASS V101 sources=%0d depth=%0d copies=%0d grants=%0d finals=%0d races=%0d reuses=%0d stalls=%0d",SOURCES,DEPTH,COPIES,grants,finals,races,immediate_reuses,stalls);
  $finish;
 end
endmodule
