// Vektor-100: multi-producer composed return fabric. Conditional on
// trusted flush_ack, exactly one FINAL per accepted request, and eventual drain.
// Reset does not establish external quiescence by itself.
module wb_multisource_composed_100 #(
 parameter integer TAG_BITS=3, DEPTH=4, SOURCES=4,
 parameter integer COPIES=3, GUARD=16, AGE_BITS=10,
 parameter integer IDX_BITS=$clog2(SOURCES), N=(1<<TAG_BITS),
 parameter integer PTR_BITS=$clog2(DEPTH)
)(
 input wire clk,cold_rst_n,soft_reset,flush_ack,offer,fabric_hold,
 input wire [N-1:0] cancel_mask,
 output wire complete,stale_drop,tag_stall,
 output wire grant_pulse,launch_fire,return_fire,return_final,
 output wire [TAG_BITS-1:0] return_tag,
 output wire [IDX_BITS-1:0] return_source,
 output wire [N-1:0] pending_mask,
 output wire [PTR_BITS:0] launch_occupancy,
 output wire [SOURCES*(PTR_BITS+1)-1:0] return_occupancies
);
 wire ready,grant,consumer_stall,ignored;
 wire [TAG_BITS-1:0] grant_tag;
 wire [N-1:0] live_mask;
 wire [PTR_BITS:0] launch_count;
 wire launch_in_ready,launch_out_valid,launch_out_ready;
 wire [TAG_BITS-1:0] launch_tag;
 wire [SOURCES-1:0] pkt_req_ready,pkt_req_valid;
 wire [SOURCES-1:0] pkt_ret_valid,pkt_ret_ready,pkt_ret_final;
 wire [SOURCES*TAG_BITS-1:0] pkt_ret_tags;
 wire [SOURCES-1:0] ret_in_ready,ret_out_valid,ret_out_ready;
 wire [SOURCES-1:0] ret_out_final;
 wire [SOURCES*TAG_BITS-1:0] ret_out_tags;
 wire [SOURCES-1:0] arb_ready;
 wire arb_valid,arb_final;
 wire [TAG_BITS-1:0] arb_tag;
 wire [IDX_BITS-1:0] arb_source;
 reg [IDX_BITS-1:0] dispatch_rr;
 reg [SOURCES-1:0] dispatch_select;
 integer k,j,dk;
 reg found;
 wire consumer_offer = offer && ready && !soft_reset &&
                       ((launch_count + (grant ? 1'b1 : 1'b0)) < DEPTH);
 wb_final_consumer_099 #(.TAG_BITS(TAG_BITS)) consumer (
  .clk(clk),.cold_rst_n(cold_rst_n),.soft_reset(soft_reset),
  .flush_ack(flush_ack),.offer(consumer_offer),.cancel_mask(cancel_mask),
  .cb_valid(return_fire),.cb_final(arb_final),.cb_tag(arb_tag),
  .grant(grant),.grant_tag(grant_tag),.complete(complete),
  .stale_drop(stale_drop),.nonfinal_ignored(ignored),
  .tag_stall(consumer_stall),.ready(ready),
  .pending_mask(pending_mask),.live_mask(live_mask)
 );
 wb_elastic_fifo_095 #(.WIDTH(TAG_BITS),.DEPTH(DEPTH)) launch_fifo (
  .clk(clk),.rst_n(cold_rst_n),.in_valid(grant),.in_ready(launch_in_ready),
  .in_data(grant_tag),.out_valid(launch_out_valid),
  .out_ready(launch_out_ready),.out_data(launch_tag),.count(launch_count)
 );
 always @* begin
  dispatch_select=0;found=0;j=0;
  for(k=0;k<SOURCES;k=k+1)begin
   j=dispatch_rr+k;
   if(j>=SOURCES)j=j-SOURCES;
   if(!found && pkt_req_ready[j])begin
    found=1;dispatch_select[j]=1;
   end
  end
 end
 assign pkt_req_valid=dispatch_select & {SOURCES{launch_out_valid}};
 assign launch_out_ready=|(pkt_req_valid & pkt_req_ready);
 always @(posedge clk or negedge cold_rst_n)begin
  if(!cold_rst_n)dispatch_rr<=0;
  else if(launch_out_valid && launch_out_ready)begin
   if(dispatch_select[SOURCES-1])dispatch_rr<=0;
   else begin
    for(dk=0;dk<SOURCES-1;dk=dk+1)
     if(dispatch_select[dk])dispatch_rr<=dk+1;
   end
  end
 end
 genvar s;
 generate for(s=0;s<SOURCES;s=s+1)begin: producers
  wire [TAG_BITS-1:0] tag;
  wire [TAG_BITS:0] ret_data;
  wire [PTR_BITS:0] ret_count;
  wb_return_packetizer_094 #(.TAG_BITS(TAG_BITS),.COPIES_BITS(4)) packetizer (
   .clk(clk),.rst_n(cold_rst_n),.req_valid(pkt_req_valid[s]),
   .req_ready(pkt_req_ready[s]),.req_tag(launch_tag),
   .req_copies(COPIES[3:0]),.ret_valid(pkt_ret_valid[s]),
   .ret_ready(pkt_ret_ready[s]),.ret_tag(tag),.ret_final(pkt_ret_final[s])
  );
  assign pkt_ret_tags[s*TAG_BITS +: TAG_BITS]=tag;
  wb_elastic_fifo_095 #(.WIDTH(TAG_BITS+1),.DEPTH(DEPTH)) return_fifo (
   .clk(clk),.rst_n(cold_rst_n),.in_valid(pkt_ret_valid[s]),
   .in_ready(ret_in_ready[s]),.in_data({pkt_ret_final[s],tag}),
   .out_valid(ret_out_valid[s]),.out_ready(ret_out_ready[s]),
   .out_data(ret_data),.count(ret_count)
  );
  assign pkt_ret_ready[s]=ret_in_ready[s];
  assign ret_out_final[s]=ret_data[TAG_BITS];
  assign ret_out_tags[s*TAG_BITS +: TAG_BITS]=ret_data[TAG_BITS-1:0];
  assign return_occupancies[s*(PTR_BITS+1) +: PTR_BITS+1]=ret_count;
 end endgenerate
 wb_return_stable_arbiter_097 #(.SOURCES(SOURCES),.TAG_BITS(TAG_BITS),
   .AGE_BITS(AGE_BITS),.GUARD(GUARD)) arbiter (
  .clk(clk),.rst_n(cold_rst_n),.src_valid(ret_out_valid),
  .src_final(ret_out_final),.src_tags(ret_out_tags),
  .sink_ready(!fabric_hold),.src_ready(arb_ready),
  .out_valid(arb_valid),.out_final(arb_final),
  .out_tag(arb_tag),.out_source(arb_source)
 );
 assign ret_out_ready=arb_ready;
 assign return_fire=arb_valid && !fabric_hold;
 assign return_final=arb_final;
 assign return_tag=arb_tag;
 assign return_source=arb_source;
 assign grant_pulse=grant;
 assign launch_fire=launch_out_valid && launch_out_ready;
 assign tag_stall=consumer_stall;
 assign launch_occupancy=launch_count;
endmodule
