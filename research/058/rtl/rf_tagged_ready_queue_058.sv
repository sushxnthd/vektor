module rf_tagged_ready_queue_058 #(
parameter integer N=4,TAGW=8,DATAW=16,REMW=2,AGEW=4,AGE_LIMIT=3,
parameter integer CW=(N>1?$clog2(N+1):1),
parameter integer IW=(N>1?$clog2(N):1)
)(
input wire clk,rst,in_valid,
output wire in_ready,
input wire [TAGW-1:0] in_tag,
input wire [DATAW-1:0] in_data,
input wire [REMW-1:0] in_remaining,
output wire out_valid,
input wire out_ready,
output wire [TAGW-1:0] out_tag,
output wire [DATAW-1:0] out_data,
output wire [CW-1:0] occupancy
);
reg [TAGW-1:0] tags[0:N-1];
reg [DATAW-1:0] data[0:N-1];
reg [REMW-1:0] rem[0:N-1];
reg [AGEW-1:0] ages[0:N-1];
reg [CW-1:0] count;
reg locked;
reg [IW-1:0] locked_idx,candidate_idx;
reg [REMW-1:0] best_rem;
reg urgent,found;
always @* begin
 candidate_idx=0;best_rem={REMW{1'b1}};urgent=0;found=0;
 for(integer k=0;k<N;k=k+1)
  if(k<count&&!urgent&&ages[k]>=AGE_LIMIT)begin candidate_idx=k;urgent=1;end
 if(!urgent)
  for(integer k=0;k<N;k=k+1)
   if(k<count&&(!found||rem[k]<best_rem))begin candidate_idx=k;best_rem=rem[k];found=1;end
end
wire [IW-1:0] select_idx=locked?locked_idx:candidate_idx;
assign out_valid=count!=0;
assign out_tag=out_valid?tags[select_idx]:0;
assign out_data=out_valid?data[select_idx]:0;
wire pop=out_valid&&out_ready;
assign in_ready=(count<N)||pop;
wire push=in_valid&&in_ready;
assign occupancy=count;
function [AGEW-1:0] inc_sat(input [AGEW-1:0] a);
begin inc_sat=(&a)?a:a+1'b1;end
endfunction
integer i;
always @(posedge clk)begin
 if(rst)begin
  count<=0;locked<=0;locked_idx<=0;
  for(i=0;i<N;i=i+1)begin tags[i]<=0;data[i]<=0;rem[i]<=0;ages[i]<=0;end
 end else begin
  if(pop)locked<=0;
  else if(out_valid&&!out_ready&&!locked)begin locked<=1;locked_idx<=select_idx;end
  case({push,pop})
   2'b10:count<=count+1'b1;
   2'b01:count<=count-1'b1;
   default:count<=count;
  endcase
  for(i=0;i<N;i=i+1)begin
   if(i<count)begin
    if(pop&&i>=select_idx&&i<count-1)begin
     tags[i]<=tags[i+1];data[i]<=data[i+1];rem[i]<=rem[i+1];ages[i]<=inc_sat(ages[i+1]);
    end else if(!pop||i<select_idx)ages[i]<=inc_sat(ages[i]);
   end
   if(push&&i==(count-(pop?1:0)))begin
    tags[i]<=in_tag;data[i]<=in_data;rem[i]<=in_remaining;ages[i]<=0;
   end
  end
 end
end
endmodule
