module v270_pack #(parameter integer MODE=1, parameter integer W=8)(
 input wire v0,v1, input wire [1:0] op0,op1,
 input wire [7:0] mask0,mask1, input wire [8*W-1:0] data0,data1,
 output wire take0,take1,issue_valid, output wire [1:0] issue_op,
 output reg [7:0] lane_valid, output reg [8*W-1:0] lane_data,
 output reg [7:0] lane_src, output reg [23:0] lane_index
);
 function [3:0] pop8;
  input [7:0] a; integer i;
  begin pop8=0; for(i=0;i<8;i=i+1) pop8=pop8+a[i]; end
 endfunction
 wire [3:0] n0=pop8(mask0), n1=pop8(mask1);
 wire [4:0] total={1'b0,n0}+{1'b0,n1};
 wire split44=(n0<=4)&&(n1<=4);
 wire split62=((n0<=6)&&(n1<=2))||((n1<=6)&&(n0<=2));
 wire eligible=v0&&v1&&(op0==op1)&&(total<=8);
 wire pair=eligible&&((MODE==0)?split44:((MODE==1)?(split44||split62):1'b1));
 assign take0=v0;
 assign take1=v1&&(!v0||pair);
 assign issue_valid=take0||take1;
 assign issue_op=v0?op0:op1;
 integer j,pos;
 always @* begin
  lane_valid=0;lane_data=0;lane_src=0;lane_index=0;pos=0;
  if(take0) for(j=0;j<8;j=j+1) if(mask0[j]) begin
   lane_valid[pos]=1'b1;
   lane_data[pos*W+:W]=data0[j*W+:W];
   lane_src[pos]=1'b0;
   lane_index[pos*3+:3]=j;
   pos=pos+1;
  end
  if(take1) for(j=0;j<8;j=j+1) if(mask1[j]) begin
   lane_valid[pos]=1'b1;
   lane_data[pos*W+:W]=data1[j*W+:W];
   lane_src[pos]=1'b1;
   lane_index[pos*3+:3]=j;
   pos=pos+1;
  end
 end
endmodule
