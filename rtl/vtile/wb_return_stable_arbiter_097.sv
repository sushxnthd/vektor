// V097: lock source after stalled beat; producer must hold data until ready.
module wb_return_stable_arbiter_097 #(
 parameter integer SOURCES=4,TAG_BITS=4,AGE_BITS=10,GUARD=16,
 parameter integer IDX_BITS=$clog2(SOURCES)
)(
 input wire clk,rst_n,
 input wire [SOURCES-1:0] src_valid,src_final,
 input wire [SOURCES*TAG_BITS-1:0] src_tags,
 input wire sink_ready,
 output reg [SOURCES-1:0] src_ready,
 output reg out_valid,out_final,
 output reg [TAG_BITS-1:0] out_tag,
 output reg [IDX_BITS-1:0] out_source
);
 reg [IDX_BITS-1:0] rr,hold_source;
 reg hold_valid;
 reg [AGE_BITS-1:0] age[0:SOURCES-1];
 integer i,k,j,choice,best;
 reg has_final;
 always @* begin
  choice=-1;best=-1;has_final=0;j=0;
  if(hold_valid) choice=hold_source;
  else begin
   for(k=0;k<SOURCES;k=k+1) begin
    j=rr+k;if(j>=SOURCES)j=j-SOURCES;
    if(src_valid[j] && age[j]>=GUARD && age[j]>best) begin
     best=age[j];choice=j;
    end
   end
   if(choice<0)begin
    for(k=0;k<SOURCES;k=k+1)begin
     j=rr+k;if(j>=SOURCES)j=j-SOURCES;
     if(src_valid[j] && src_final[j] && !has_final)begin
      choice=j;has_final=1;
     end
    end
    if(!has_final)for(k=0;k<SOURCES;k=k+1)begin
     j=rr+k;if(j>=SOURCES)j=j-SOURCES;
     if(src_valid[j] && choice<0)choice=j;
    end
   end
  end
  src_ready=0;out_valid=0;out_final=0;out_tag=0;out_source=0;
  if(choice>=0)begin
   out_valid=src_valid[choice];out_source=choice;
   out_final=src_final[choice];
   out_tag=src_tags[choice*TAG_BITS +: TAG_BITS];
   if(sink_ready && out_valid)src_ready[choice]=1;
  end
 end
 always @(posedge clk or negedge rst_n)begin
  if(!rst_n)begin
   rr<=0;hold_valid<=0;hold_source<=0;
   for(i=0;i<SOURCES;i=i+1)age[i]<=0;
  end else begin
   if(out_valid && !sink_ready && !hold_valid)begin
    hold_valid<=1;hold_source<=out_source;
   end
   if(out_valid && sink_ready)begin
    hold_valid<=0;
    if(out_source==SOURCES-1)rr<=0;else rr<=out_source+1'b1;
   end
   for(i=0;i<SOURCES;i=i+1)begin
    if(!src_valid[i] || src_ready[i])age[i]<=0;
    else if(age[i]!={AGE_BITS{1'b1}})age[i]<=age[i]+1'b1;
   end
  end
 end
endmodule
