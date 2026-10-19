`timescale 1ns/1ps
module tb_compact;
reg [7:0] tag; reg [3:0] mask; reg [31:0] valid; reg [255:0] tags;
wire [31:0] a,b;
integer t,j;
v232_control x(tag,mask,valid,tags,a);
v232_selective y(tag,mask,valid,tags,b);
initial begin
tag=0;mask=0;valid=0;tags=0;
for(t=0;t<8192;t=t+1)begin
tag=$random;mask=$random;valid=$random;
for(j=0;j<8;j=j+1)tags[32*j+:32]=$random;
#1;
if(a!==b)begin $display("FAIL %0d",t);$fatal(1);end
end
$display("PASS 8192");$finish;
end
endmodule
