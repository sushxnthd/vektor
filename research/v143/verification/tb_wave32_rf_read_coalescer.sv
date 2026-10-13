`timescale 1ns/1ps
module tb_wave32_rf_read_coalescer;
 localparam integer WIDTH=1024;
 reg [17:0] src_regs;
 reg [2:0] missing,rf_rsp_valid;
 reg req_valid;
 reg [3*WIDTH-1:0] rf_rsp_data;
 wire [2:0] rf_req,src_rsp_valid;
 wire [3*WIDTH-1:0] src_rsp_data;
 integer trial,i,j,lane;
 reg [2:0] expected_req,expected_valid;
 reg duplicate;
 reg [WIDTH-1:0] expected_data;
 vektor_wave32_rf_read_coalescer dut(
 .src_regs(src_regs),.missing(missing),.req_valid(req_valid),.rf_req(rf_req),
 .rf_rsp_valid(rf_rsp_valid),.rf_rsp_data(rf_rsp_data),
 .src_rsp_valid(src_rsp_valid),.src_rsp_data(src_rsp_data));
 initial begin
  for(trial=0;trial<800;trial=trial+1) begin
   for(i=0;i<3;i=i+1) begin
    if(trial%4==0)src_regs[i*6 +:6]=6'd12;
    else if(trial%4==1)src_regs[i*6 +:6]=(i==2)?6'd19:6'd12;
    else if(trial%4==2)src_regs[i*6 +:6]=6'd12+i;
    else src_regs[i*6 +:6]=$random;
    for(lane=0;lane<32;lane=lane+1)
     rf_rsp_data[i*WIDTH+lane*32 +:32]=32'h9e3779b9 ^ (trial*127+i*8191+lane);
   end
   missing=$random;req_valid=$random;rf_rsp_valid=$random;
   #1;
   expected_req=0;expected_valid=0;
   for(i=0;i<3;i=i+1) begin
    duplicate=0;
    for(j=0;j<i;j=j+1)
     if(missing[j] && src_regs[i*6 +:6]==src_regs[j*6 +:6])duplicate=1;
    if(req_valid && missing[i] && !duplicate)expected_req[i]=1;
   end
   if(rf_req!==expected_req)$fatal(1,"request mismatch trial=%0d",trial);
   for(i=0;i<3;i=i+1) begin
    expected_data=0;
    for(j=0;j<3;j=j+1)
     if(missing[i] && !expected_valid[i] && rf_rsp_valid[j] &&
        src_regs[i*6 +:6]==src_regs[j*6 +:6]) begin
       expected_valid[i]=1;
       expected_data=rf_rsp_data[j*WIDTH +: WIDTH];
     end
    if(src_rsp_data[i*WIDTH +: WIDTH]!==expected_data)
     $fatal(1,"response data mismatch trial=%0d src=%0d",trial,i);
   end
   if(src_rsp_valid!==expected_valid)$fatal(1,"response valid mismatch trial=%0d",trial);
  end
  $display("V143 PASS: 800 full-Wave32 RTL response/request test vectors");
  $finish;
 end
endmodule
