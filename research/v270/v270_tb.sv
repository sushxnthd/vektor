module v270_tb;
 reg v0,v1;reg [1:0] op0,op1;reg [7:0] mask0,mask1;reg [63:0] data0,data1;
 wire [2:0] take0,take1,valid;
 wire [1:0] op[0:2];
 wire [7:0] lane_valid[0:2],lane_src[0:2];
 wire [63:0] lane_data[0:2];wire [23:0] lane_index[0:2];
 v270_pack #(.MODE(0)) s(v0,v1,op0,op1,mask0,mask1,data0,data1,take0[0],take1[0],valid[0],op[0],lane_valid[0],lane_data[0],lane_src[0],lane_index[0]);
 v270_pack #(.MODE(1)) a(v0,v1,op0,op1,mask0,mask1,data0,data1,take0[1],take1[1],valid[1],op[1],lane_valid[1],lane_data[1],lane_src[1],lane_index[1]);
 v270_pack #(.MODE(2)) f(v0,v1,op0,op1,mask0,mask1,data0,data1,take0[2],take1[2],valid[2],op[2],lane_valid[2],lane_data[2],lane_src[2],lane_index[2]);
 integer t,m,i,p,n0,n1,expected_pair,expected_take1;
 initial begin
  data0=0;data1=0;
  for(i=0;i<8;i=i+1) begin data0[8*i+:8]=i+1;data1[8*i+:8]=i+17;end
  for(t=0;t<12000;t=t+1) begin
   v0=($random&7)!=0;v1=($random&7)!=0;
   mask0=$random;mask1=$random;op0=$random;op1=$random;
   #1;n0=0;n1=0;
   for(i=0;i<8;i=i+1) begin n0=n0+mask0[i];n1=n1+mask1[i];end
   for(m=0;m<3;m=m+1) begin
    expected_pair=v0&&v1&&(op0==op1)&&(n0+n1<=8)&&
      ((m==2)||((n0<=4)&&(n1<=4))||((m==1)&&(((n0<=6)&&(n1<=2))||((n1<=6)&&(n0<=2)))));
    expected_take1=v1&&(!v0||expected_pair);
    if(take0[m]!==v0 || take1[m]!==expected_take1 || valid[m] !== (v0||expected_take1)) $fatal(1,"grant mismatch t=%0d mode=%0d",t,m);
    if(valid[m] && op[m] !== (v0?op0:op1)) $fatal(1,"opcode mismatch");
    p=0;
    if(v0) for(i=0;i<8;i=i+1) if(mask0[i]) begin
     if(!lane_valid[m][p] || lane_src[m][p]!==0 || lane_index[m][p*3+:3]!==i || lane_data[m][p*8+:8]!==i+1) $fatal(1,"warp0 mismatch");
     p=p+1;
    end
    if(expected_take1) for(i=0;i<8;i=i+1) if(mask1[i]) begin
     if(!lane_valid[m][p] || lane_src[m][p]!==1 || lane_index[m][p*3+:3]!==i || lane_data[m][p*8+:8]!==i+17) $fatal(1,"warp1 mismatch");
     p=p+1;
    end
    if(lane_valid[m] !== ((1<<p)-1)) $fatal(1,"valid mismatch");
   end
  end
  $display("PASS V270 12000 trials x3 modes");$finish;
 end
endmodule
