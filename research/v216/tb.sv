`timescale 1ns/1ps
module tb_v216;
  reg valid; reg [4:0] wave; reg [7:0] tag;
  reg [127:0] pending; reg [1023:0] entry_tags;
  wire [127:0] a,b; integer i,j;
  vektor_wakeup_predecoded u0(valid,wave,tag,pending,entry_tags,a);
  vektor_wakeup_isolated u1(valid,wave,tag,pending,entry_tags,b);
  initial begin
    valid=0; wave=0; tag=0; pending=0; entry_tags=0;
    for(i=0;i<10000;i=i+1) begin
      valid=$random; wave=$random; tag=$random;
      for(j=0;j<4;j=j+1) pending[j*32 +: 32]=$random;
      for(j=0;j<32;j=j+1) entry_tags[j*32 +: 32]=$random;
      if(i%4==0) entry_tags[wave*32 +: 8]=tag;
      #1;
      if(a !== b) $fatal(1,"mismatch at vector %0d",i);
    end
    $display("PASS 10000 differential vectors");
    $finish;
  end
endmodule
