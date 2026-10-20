// V254 research functional check; iverilog -g2012 -s tb_v254_rf ...
module tb_v254_rf;
 reg clk=0; always #5 clk=~clk;
 reg wr=0, ren=0, ren0=0, ren1=0;
 reg [1:0] wmask=0;
 reg [5:0] waddr=0, raddr=0, raddr0=0, raddr1=0;
 reg [31:0] wdata=0;
 wire [31:0] mdata;
 wire [15:0] s0,s1;
 reg [31:0] refmem [0:63];
 integer i,j;
 v254_mono_rf mono(clk,wr,wmask,waddr,wdata,ren,raddr,mdata);
 v254_split_rf split(clk,wr,wmask,waddr,wdata,ren0,ren1,raddr0,raddr1,s0,s1);
 initial begin
  for(i=0;i<64;i=i+1) begin
   @(negedge clk);
   wr=1; wmask=2'b11; waddr=i;
   wdata=(32'h9e3779b9 ^ (i*32'h00010203));
   refmem[i]=wdata;
  end
  @(negedge clk); wr=0; ren=1; ren0=1; ren1=1;
  for(i=0;i<64;i=i+1) begin
   raddr=i; raddr0=i; raddr1=i; #1;
   if(mdata !== refmem[i] || {s1,s0} !== refmem[i]) $fatal(1,"wide mismatch i=%0d",i);
  end
  // Different physical addresses: split returns both narrow operands in one service cycle.
  for(i=0;i<64;i=i+1) begin
   raddr0=i; raddr1=(i+17)%64; #1;
   if(s0 !== refmem[i][15:0] || s1 !== refmem[(i+17)%64][31:16])
     $fatal(1,"dual-narrow mismatch i=%0d",i);
  end
  // Masked write must preserve the other half, including at the wide-read interface.
  @(negedge clk); wr=1; wmask=2'b01; waddr=7; wdata=32'hdeadbeef;
  refmem[7][15:0]=16'hbeef;
  @(negedge clk); wr=0; raddr=7; raddr0=7; raddr1=7; #1;
  if(mdata !== refmem[7] || {s1,s0} !== refmem[7]) $fatal(1,"masked write mismatch");
  $display("V254_PASS wide=64 dual_narrow=64 masked_write=1");
  $finish;
 end
endmodule
