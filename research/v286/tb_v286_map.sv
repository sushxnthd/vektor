`timescale 1ns/1ps
module tb_v286_map;
 reg [3:0] logical_bank,warp_id_low;
 wire [3:0] add_bank,xor_bank;
 integer w,b,b2;
 reg [15:0] seen_add,seen_xor;
 v286_add_bank_map a(logical_bank,warp_id_low,add_bank);
 v286_xor_bank_map x(logical_bank,warp_id_low,xor_bank);
 initial begin
  for(w=0;w<16;w=w+1)begin
   seen_add=0;seen_xor=0;
   for(b=0;b<16;b=b+1)begin
    logical_bank=b;warp_id_low=w;#1;
    if(seen_add[add_bank] || seen_xor[xor_bank])$fatal(1,"non-bijective bank mapping warp %0d reg %0d",w,b);
    seen_add[add_bank]=1;seen_xor[xor_bank]=1;
    b2=(add_bank-w)&15;
    if(b2!=b || ((xor_bank^w)!=b))$fatal(1,"read/write map invertibility failed");
   end
   if(seen_add!==16'hffff || seen_xor!==16'hffff)$fatal(1,"incomplete permutation");
  end
  $display("PASS V286 exhaustive 256 bank map permutations");
  $finish;
 end
endmodule
