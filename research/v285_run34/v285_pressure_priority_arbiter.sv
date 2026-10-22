module v285_pressure_priority_arbiter (
 input wire [3:0] request_valid,
 input wire [15:0] src0_bank_flat,
 input wire [15:0] src1_bank_flat,
 output reg [3:0] grant
);
 integer score[0:3];
 integer i,j,step,sel,best;
 reg [3:0] seen;
 reg [3:0] b0,b1;
 reg [15:0] used_once,used_twice,mask0,mask1;
 always @* begin
  for(i=0;i<4;i=i+1)begin
   score[i]=0;
   if(request_valid[i])begin
    for(j=0;j<4;j=j+1)begin
     if(request_valid[j])begin
      if(src0_bank_flat[4*i +:4]==src0_bank_flat[4*j +:4])score[i]=score[i]+1;
      if(src0_bank_flat[4*i +:4]==src1_bank_flat[4*j +:4])score[i]=score[i]+1;
      if(src1_bank_flat[4*i +:4]==src0_bank_flat[4*j +:4])score[i]=score[i]+1;
      if(src1_bank_flat[4*i +:4]==src1_bank_flat[4*j +:4])score[i]=score[i]+1;
     end
    end
   end
  end
  grant=0;seen=0;used_once=0;used_twice=0;
  b0=0;b1=0;mask0=0;mask1=0;best=99;sel=-1;
  for(step=0;step<4;step=step+1)begin
   best=99;sel=-1;
   for(i=0;i<4;i=i+1)begin
    if(request_valid[i] && !seen[i] && score[i]<best)begin
     best=score[i];sel=i;
    end
   end
   if(sel>=0)begin
    seen[sel]=1'b1;
    b0=src0_bank_flat[4*sel +:4];
    b1=src1_bank_flat[4*sel +:4];
    mask0=16'b1<<b0;mask1=16'b1<<b1;
    if(b0==b1)begin
     if(!( |(used_once&mask0)))begin
      grant[sel]=1'b1;
      used_once=used_once|mask0;
      used_twice=used_twice|mask0;
     end
    end else if(!( |(used_twice&mask0)) && !( |(used_twice&mask1)))begin
     grant[sel]=1'b1;
     if(|(used_once&mask0))used_twice=used_twice|mask0;
     else used_once=used_once|mask0;
     if(|(used_once&mask1))used_twice=used_twice|mask1;
     else used_once=used_once|mask1;
    end
   end
  end
 end
endmodule
