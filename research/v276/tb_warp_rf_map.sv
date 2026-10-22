
`timescale 1ns/1ps
module tb_warp_rf_map;
reg clk=0; always #5 clk=~clk;
reg rst=1,alloc_en=0,alloc_mode=0,valid0=0,valid1=0;
reg [1:0] alloc_warp=0,warp0=0,warp1=0,warpw=0;
reg [5:0] reg0=0,reg1=0,regw=0;
wire [1:0] a0,a1,aw,d0,d1,dw,x0,x1,xw;
wire [5:0] ar0,ar1,arw,dr0,dr1,drw,xr0,xr1,xrw;
wire ag0,ag1,dg0,dg1,xg0,xg1;
reg [3:0] modes=0;
integer seed=27623,i;
function [1:0] h(input [5:0] r,input m);
 h=r[1:0]^(r[3:2]&{2{m}});
endfunction
v276_warp_rf_map #(.ADAPTIVE(1)) a(clk,rst,alloc_en,alloc_warp,alloc_mode,valid0,valid1,warp0,warp1,warpw,reg0,reg1,regw,a0,a1,aw,ar0,ar1,arw,ag0,ag1);
v276_warp_rf_map #(.ADAPTIVE(0),.FIXED_MODE(0)) d(clk,rst,alloc_en,alloc_warp,alloc_mode,valid0,valid1,warp0,warp1,warpw,reg0,reg1,regw,d0,d1,dw,dr0,dr1,drw,dg0,dg1);
v276_warp_rf_map #(.ADAPTIVE(0),.FIXED_MODE(1)) x(clk,rst,alloc_en,alloc_warp,alloc_mode,valid0,valid1,warp0,warp1,warpw,reg0,reg1,regw,x0,x1,xw,xr0,xr1,xrw,xg0,xg1);
initial begin
 @(negedge clk); rst=0;
 for(i=0;i<50000;i=i+1) begin
  @(negedge clk);
  alloc_en=($unsigned($random(seed))%31==0);
  alloc_warp=$unsigned($random(seed))%4;
  alloc_mode=$unsigned($random(seed))%2;
  warp0=$unsigned($random(seed))%4;
  warp1=$unsigned($random(seed))%4;
  warpw=$unsigned($random(seed))%4;
  reg0=$unsigned($random(seed))%64;
  reg1=$unsigned($random(seed))%64;
  regw=$unsigned($random(seed))%64;
  valid0=$unsigned($random(seed))%2;
  valid1=$unsigned($random(seed))%2;
  @(posedge clk); #1;
  if(alloc_en) modes[alloc_warp]=alloc_mode;
  if(a0!==h(reg0,modes[warp0]) || a1!==h(reg1,modes[warp1]) || aw!==h(regw,modes[warpw]) ||
     d0!==h(reg0,1'b0) || d1!==h(reg1,1'b0) || dw!==h(regw,1'b0) ||
     x0!==h(reg0,1'b1) || x1!==h(reg1,1'b1) || xw!==h(regw,1'b1) ||
     ar0!=={warp0,reg0[5:2]} || ar1!=={warp1,reg1[5:2]} || arw!=={warpw,regw[5:2]} ||
     dr0!==ar0 || dr1!==ar1 || drw!==arw || xr0!==ar0 || xr1!==ar1 || xrw!==arw ||
     ag0!==valid0 || ag1!==(valid1&&(!valid0||a0!=a1)) ||
     dg0!==valid0 || dg1!==(valid1&&(!valid0||d0!=d1)) ||
     xg0!==valid0 || xg1!==(valid1&&(!valid0||x0!=x1)))
   $fatal(1,"V276 mismatch at cycle %0d",i);
 end
 $display("V276 PASS: 50000 RTL checks across candidate and two fixed controls");
 $finish;
end
endmodule
