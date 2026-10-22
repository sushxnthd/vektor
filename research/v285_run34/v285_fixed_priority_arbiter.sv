module v285_fixed_priority_arbiter (
 input wire [3:0] request_valid,
 input wire [15:0] src0_bank_flat,
 input wire [15:0] src1_bank_flat,
 output reg [3:0] grant
);
 integer i;
 reg [3:0] a,b;
 reg [15:0] once,twice,ma,mb;
 always @* begin
  grant=0;once=0;twice=0;a=0;b=0;ma=0;mb=0;
  for(i=0;i<4;i=i+1)begin
   a=src0_bank_flat[4*i +:4];
   b=src1_bank_flat[4*i +:4];
   ma=16'b1<<a;mb=16'b1<<b;
   if(request_valid[i])begin
    if(a==b)begin
     if(!( |(once&ma)))begin
      grant[i]=1'b1;once=once|ma;twice=twice|ma;
     end
    end else if(!( |(twice&ma)) && !( |(twice&mb)))begin
     grant[i]=1'b1;
     if(|(once&ma))twice=twice|ma;
     else once=once|ma;
     if(|(once&mb))twice=twice|mb;
     else once=once|mb;
    end
   end
  end
 end
endmodule
