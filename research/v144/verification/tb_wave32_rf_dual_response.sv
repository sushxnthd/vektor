`timescale 1ns/1ps
module tb_wave32_rf_dual_response;
localparam integer WIDTH=1024;
reg [17:0] src_regs;
reg [2:0] missing;
reg [1:0] rf_rsp_valid;
reg [11:0] rf_rsp_reg;
reg [7:0] rf_rsp_bank;
reg [2*WIDTH-1:0] rf_rsp_data;
wire [1:0] rf_rsp_accept;
wire [2:0] src_rsp_valid;
wire [3*WIDTH-1:0] src_rsp_data;
reg [1:0] expect_accept;
reg [2:0] expect_valid;
reg [WIDTH-1:0] expect_data;
integer trial,i,lane;
vektor_wave32_rf_dual_response dut(
 .src_regs(src_regs),.missing(missing),.rf_rsp_valid(rf_rsp_valid),
 .rf_rsp_reg(rf_rsp_reg),.rf_rsp_bank(rf_rsp_bank),.rf_rsp_data(rf_rsp_data),
 .rf_rsp_accept(rf_rsp_accept),.src_rsp_valid(src_rsp_valid),.src_rsp_data(src_rsp_data));
initial begin
 for(trial=0;trial<1200;trial=trial+1) begin
  for(i=0;i<3;i=i+1) begin
   if(trial%4==0) src_regs[i*6 +:6]=6'd12;
   else if(trial%4==1) src_regs[i*6 +:6]=(i==2)?6'd19:6'd12;
   else if(trial%4==2) src_regs[i*6 +:6]=6'd12+i;
   else src_regs[i*6 +:6]=$random;
  end
  rf_rsp_reg[0 +:6]=(trial%3==0)?src_regs[0 +:6]:$random;
  rf_rsp_reg[6 +:6]=(trial%3==0)?src_regs[12 +:6]:$random;
  rf_rsp_bank[0 +:4]=(trial%4==0)?4'd3:$random;
  rf_rsp_bank[4 +:4]=(trial%4==0)?4'd3:$random;
  missing=$random;
  rf_rsp_valid=$random;
  for(lane=0;lane<32;lane=lane+1) begin
   rf_rsp_data[lane*32 +:32]=32'h9abc0000 ^ (trial*67+lane);
   rf_rsp_data[WIDTH+lane*32 +:32]=32'h56780000 ^ (trial*131+lane);
  end
  #1;
  expect_accept[0]=rf_rsp_valid[0];
  expect_accept[1]=rf_rsp_valid[1] && !(rf_rsp_valid[0] && rf_rsp_bank[0 +:4]==rf_rsp_bank[4 +:4]);
  expect_valid=0;
  if(rf_rsp_accept!==expect_accept) $fatal(1,"bank arbitration mismatch %0d",trial);
  for(i=0;i<3;i=i+1) begin
   expect_data=0;
   if(missing[i] && expect_accept[0] && src_regs[i*6 +:6]==rf_rsp_reg[0 +:6])begin
     expect_valid[i]=1;
     expect_data=rf_rsp_data[0 +:WIDTH];
   end
   if(missing[i] && expect_accept[1] && src_regs[i*6 +:6]==rf_rsp_reg[6 +:6])begin
     expect_valid[i]=1;
     expect_data=rf_rsp_data[WIDTH +:WIDTH];
   end
   if(src_rsp_data[i*WIDTH +:WIDTH]!==expect_data)
      $fatal(1,"Wave32 data mismatch trial=%0d slot=%0d",trial,i);
  end
  if(src_rsp_valid!==expect_valid)$fatal(1,"valid mismatch trial=%0d",trial);
 end
 $display("V144 PASS: 1200 full-Wave32 dual-bank response vectors");
 $finish;
end
endmodule
