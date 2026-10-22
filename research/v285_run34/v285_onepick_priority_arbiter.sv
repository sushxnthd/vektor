// V285 one-repair implementation: first request chosen by lowest aggregate
// bank pressure; all remaining requests in original order. Same four inputs,
// 16 banks, two read slots/bank, no extra ports or queues.
module v285_onepick_priority_arbiter (
 input wire [3:0] request_valid,
 input wire [15:0] src0_bank_flat,
 input wire [15:0] src1_bank_flat,
 output reg [3:0] grant
);
 reg [3:0] score[0:3];
 reg [3:0] best;
 reg [1:0] first,sel;
 reg found;
 reg [3:0] b0,b1;
 reg [15:0] once,twice,m0,m1;
 integer i,j,step;
 always @* begin
  for(i=0;i<4;i=i+1)begin
   score[i]=0;
   for(j=0;j<4;j=j+1)begin
    if(request_valid[j])begin
     score[i]=score[i]+(src0_bank_flat[4*i +:4]==src0_bank_flat[4*j +:4]);
     score[i]=score[i]+(src0_bank_flat[4*i +:4]==src1_bank_flat[4*j +:4]);
     score[i]=score[i]+(src1_bank_flat[4*i +:4]==src0_bank_flat[4*j +:4]);
     score[i]=score[i]+(src1_bank_flat[4*i +:4]==src1_bank_flat[4*j +:4]);
    end
   end
  end
  best=4'd15;first=0;found=0;
  for(i=0;i<4;i=i+1)begin
   if(request_valid[i] && (!found || score[i]<best))begin
    best=score[i];first=i;found=1;
   end
  end
  grant=0;once=0;twice=0;m0=0;m1=0;b0=0;b1=0;sel=0;
  for(step=0;step<5;step=step+1)begin
   if(step==0)sel=first;
   else sel=step-1;
   if((step!=0 || found) && (step==0 || sel!=first) && request_valid[sel])begin
    b0=src0_bank_flat[4*sel +:4];
    b1=src1_bank_flat[4*sel +:4];
    m0=16'b1<<b0;m1=16'b1<<b1;
    if(b0==b1)begin
     if(!( |(once&m0)))begin
      grant[sel]=1'b1;once=once|m0;twice=twice|m0;
     end
    end else if(!( |(twice&m0)) && !( |(twice&m1)))begin
     grant[sel]=1'b1;
     if(|(once&m0))twice=twice|m0;
     else once=once|m0;
     if(|(once&m1))twice=twice|m1;
     else once=once|m1;
    end
   end
  end
 end
endmodule
