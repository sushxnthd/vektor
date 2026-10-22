`timescale 1ns/1ps
module tb_v286_permuted;
 reg [3:0] logical_bank,warp_id_low;
 wire [3:0] p;
 reg [15:0] seen;
 integer w,b;
 v286_permuted_bank_map dut(logical_bank,warp_id_low,p);
 initial begin
  for(w=0;w<16;w=w+1)begin
   seen=0;
   for(b=0;b<16;b=b+1)begin
    warp_id_low=w;logical_bank=b;#1;
    if(seen[p])$fatal(1,"non-bijective mapping warp %0d bank %0d",w,b);
    seen[p]=1;
    if((p ^ {warp_id_low[2:0],warp_id_low[3]}) != b)$fatal(1,"write/read inverse failed");
   end
   if(seen!==16'hffff)$fatal(1,"incomplete mapping");
  end
  $display("PASS V286 permuted map 256 exhaustive cases");
  $finish;
 end
endmodule
