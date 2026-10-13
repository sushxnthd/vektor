`timescale 1ns/1ps
module tb_wave32_rf_parity_fixed;
localparam integer W=1024;
reg [17:0] src_regs;
reg [2:0] missing;
reg [1:0] rf_rsp_valid;
reg [11:0] rf_rsp_reg;
reg [7:0] rf_rsp_bank;
reg [2*W-1:0] rf_rsp_data;
wire [1:0] fixed_accept,flex_accept;
wire [2:0] fixed_valid,flex_valid;
wire [3*W-1:0] fixed_data,flex_data;
integer trial,slot,lane;
reg [5:0] even_reg,odd_reg;
vektor_wave32_rf_parity_fixed fixed_dut(
 .src_regs(src_regs),.missing(missing),.rf_rsp_valid(rf_rsp_valid),
 .rf_rsp_reg(rf_rsp_reg),.rf_rsp_bank(rf_rsp_bank),.rf_rsp_data(rf_rsp_data),
 .rf_rsp_accept(fixed_accept),.src_rsp_valid(fixed_valid),.src_rsp_data(fixed_data));
vektor_wave32_rf_dual_response flexible_dut(
 .src_regs(src_regs),.missing(missing),.rf_rsp_valid(rf_rsp_valid),
 .rf_rsp_reg(rf_rsp_reg),.rf_rsp_bank(rf_rsp_bank),.rf_rsp_data(rf_rsp_data),
 .rf_rsp_accept(flex_accept),.src_rsp_valid(flex_valid),.src_rsp_data(flex_data));
initial begin
 for(trial=0;trial<1600;trial=trial+1)begin
  even_reg=2*($random & 31);
  odd_reg=2*($random & 31)+1;
  rf_rsp_reg={odd_reg,even_reg};
  rf_rsp_bank={odd_reg[3:0],even_reg[3:0]};
  rf_rsp_valid=$random;missing=$random;
  for(slot=0;slot<3;slot=slot+1)begin
   case((trial+slot)%4)
    0:src_regs[slot*6 +:6]=even_reg;
    1:src_regs[slot*6 +:6]=odd_reg;
    2:src_regs[slot*6 +:6]=$random;
    3:src_regs[slot*6 +:6]=even_reg;
   endcase
  end
  for(lane=0;lane<32;lane=lane+1)begin
   rf_rsp_data[lane*32 +:32]=32'hcafe0000 ^ (trial*67+lane);
   rf_rsp_data[W+lane*32 +:32]=32'hface0000 ^ (trial*131+lane);
  end
  #1;
  if(fixed_accept!==flex_accept || fixed_valid!==flex_valid || fixed_data!==flex_data)
    $fatal(1,"legal parity mismatch trial=%0d",trial);
  if(trial%8==0)begin
    rf_rsp_bank[0]=1'b1; #1;
    if(fixed_accept[0]!==1'b0)$fatal(1,"invalid even port accepted %0d",trial);
  end
  if(trial%8==1)begin
    rf_rsp_bank[4]=1'b0; #1;
    if(fixed_accept[1]!==1'b0)$fatal(1,"invalid odd port accepted %0d",trial);
  end
 end
 $display("V145 PASS: 1600 legal full-Wave32 differential + parity-negative tests");
 $finish;
end
endmodule
