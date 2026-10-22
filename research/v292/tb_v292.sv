module tb_v292;
reg va,vb; reg [1:0] credits;
reg [31:0] ma,mb;
reg [1023:0] da,db;
reg [15:0] ta,tb;
wire aa,ab;
wire [1023:0] dout;
wire [31:0] oa,ob;
wire [15:0] ota,otb;
integer i,j,checks;
reg expect_a,expect_b;
reg [31:0] expect_lane;
v292_sparse_return_overlay dut(
 .valid_a(va),.valid_b(vb),.collector_credits(credits),
 .mask_a(ma),.mask_b(mb),.data_a(da),.data_b(db),
 .tag_a(ta),.tag_b(tb),.accept_a(aa),.accept_b(ab),
 .data_out(dout),.out_mask_a(oa),.out_mask_b(ob),
 .out_tag_a(ota),.out_tag_b(otb)
);
initial begin
 checks=0;va=0;vb=0;credits=0;ma=0;mb=0;da=0;db=0;ta=0;tb=0;
 for(i=0;i<6000;i=i+1) begin
  va=(i%13)!=0; vb=(i%11)!=0; credits=i%3;
  ma=(i*32'h9e3779b9) ^ 32'h00ff00ff;
  mb=(i*32'h7f4a7c15) ^ 32'hf0f00f0f;
  if(i%4==0) mb=~ma;
  if(i%7==0) mb=ma;
  ta=i;tb=i+1;
  for(j=0;j<32;j=j+1) begin
    da[j*32 +:32] = i*101+j;
    db[j*32 +:32] = i*103+j+32'h80000000;
  end
  #1;
  expect_a=va && (credits!=0);
  expect_b=expect_a && vb && ((ma&mb)==0) && credits>=2;
  if(aa!==expect_a || ab!==expect_b ||
     oa!==(expect_a?ma:32'b0) || ob!==(expect_b?mb:32'b0) ||
     ota!==(expect_a?ta:16'b0) || otb!==(expect_b?tb:16'b0))
     $fatal(1,"V292 handshake/mask mismatch i=%0d",i);
  for(j=0;j<32;j=j+1) begin
    expect_lane=(expect_a && ma[j])?da[j*32 +:32]:
                (expect_b && mb[j])?db[j*32 +:32]:32'b0;
    if(dout[j*32 +:32] !== expect_lane)
      $fatal(1,"V292 lane data mismatch i=%0d lane=%0d",i,j);
  end
  checks=checks+1;
 end
 $display("V292 RTL SMOKE PASS checks=%0d",checks);
 $finish;
end
endmodule
