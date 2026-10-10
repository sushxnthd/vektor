// Vektor-094 final-only tag retirement. Requires exactly one FINAL
// beat per transaction and a flushed return path on cold reset.
// Soft reset cancels live work but preserves pending tag ownership.
// No internal proof that an external FINAL belongs to the right uid.
module wb_final_consumer_094 #(
 parameter integer TAG_BITS=3,N=(1<<TAG_BITS)
)(
 input wire clk,cold_rst_n,soft_reset,flush_ack,offer,
 input wire [N-1:0] cancel_mask,
 input wire cb_valid,cb_final,
 input wire [TAG_BITS-1:0] cb_tag,
 output reg grant,
 output reg [TAG_BITS-1:0] grant_tag,
 output reg complete,stale_drop,nonfinal_ignored,tag_stall,ready,
 output reg [N-1:0] pending_mask,live_mask
);
 reg [TAG_BITS-1:0] rr;
 reg [N-1:0] pending_next,live_next;
 reg choice_valid,cb_live_match;
 reg [TAG_BITS-1:0] choice,candidate;
 integer k;
 always @* begin
  pending_next=pending_mask;
  live_next=live_mask;
  cb_live_match=0;
  if(cb_valid&&cb_final) begin
   cb_live_match=pending_mask[cb_tag]&&live_mask[cb_tag];
   pending_next[cb_tag]=0;live_next[cb_tag]=0;
  end
  if(soft_reset) live_next=0;
  else live_next=live_next&~cancel_mask;
  choice_valid=0;choice=rr;candidate=rr;
  for(k=0;k<N;k=k+1) begin
   candidate=rr+k;
   if(!choice_valid&&!pending_next[candidate]) begin
    choice_valid=1;choice=candidate;
   end
  end
  if(ready&&!soft_reset&&offer&&choice_valid) begin
   pending_next[choice]=1;live_next[choice]=1;
  end
 end
 always @(posedge clk or negedge cold_rst_n) begin
  if(!cold_rst_n) begin
   rr<=0;ready<=0;pending_mask<=0;live_mask<=0;
   grant<=0;grant_tag<=0;complete<=0;stale_drop<=0;
   nonfinal_ignored<=0;tag_stall<=0;
  end else begin
   if(flush_ack)ready<=1;
   pending_mask<=pending_next;live_mask<=live_next;
   grant<=ready&&!soft_reset&&offer&&choice_valid;
   if(ready&&!soft_reset&&offer&&choice_valid) begin
    grant_tag<=choice;rr<=choice+1'b1;
   end
   complete<=cb_valid&&cb_final&&cb_live_match&&!soft_reset;
   stale_drop<=cb_valid&&cb_final&&!(cb_live_match&&!soft_reset);
   nonfinal_ignored<=cb_valid&&!cb_final;
   tag_stall<=ready&&!soft_reset&&offer&&!choice_valid;
  end
 end
endmodule
