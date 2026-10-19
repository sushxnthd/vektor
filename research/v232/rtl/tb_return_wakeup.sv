`timescale 1ns/1ps
module tb_return_wakeup;
reg rv; reg [7:0] tag; reg [3:0] mask;
reg [31:0] valid; reg [255:0] tags;
wire [31:0] control, candidate;
integer t,j;
v232_return_wakeup_control a(rv,tag,mask,valid,tags,control);
v232_return_wakeup_selective b(rv,tag,mask,valid,tags,candidate);
initial begin
 rv=0;tag=0;mask=0;valid=0;tags=0;
 for(t=0;t<8192;t=t+1) begin
  rv=$random;tag=$random;mask=$random;valid=$random;
  for(j=0;j<8;j=j+1) tags[32*j +: 32]=$random;
  #1;
  if(control !== candidate) begin $display("MISMATCH %0d",t); $fatal(1); end
 end
 $display("PASS 8192 RTL vectors");$finish;
end
endmodule
