`timescale 1ns/1ps
module tb;
reg [63:0] a_addr=0,b_addr=0;
reg [4:0] a_size=1,b_size=1;
reg [1:0] a_space=0,b_space=0;
reg [15:0] a_cta=0,b_cta=0;
reg [31:0] a_tid=0,b_tid=0;
reg a_write=1,b_write=0;
wire a_valid,b_valid,hazard;
scoped_byte_hazard dut(.*);
integer checks=0;
task check(input bit expected);
begin
#1;
if(hazard !== expected) $fatal(1,"hazard mismatch at check %0d",checks);
checks=checks+1;
end
endtask
initial begin
a_addr=64'h1000;b_addr=64'h1004;a_size=8;b_size=4;
a_space=0;b_space=0;check(1);
b_addr=64'h1008;check(0);
b_addr=64'h1004;a_space=1;b_space=1;a_cta=0;b_cta=1;check(0);
b_cta=0;check(1);
a_space=2;b_space=2;a_tid=0;b_tid=1;check(0);
b_tid=0;check(1);
a_space=0;b_space=1;check(0);
a_space=0;b_space=0;a_write=0;b_write=0;check(0);
a_write=1;a_addr=64'hfffffffffffffff0;b_addr=64'hfffffffffffffff8;
a_size=16;b_size=8;check(1);
a_size=16;b_size=16;check(0);
a_addr=64'hffffffffffffffff;a_size=1;b_addr=64'hffffffffffffffff;b_size=1;check(1);
a_size=2;check(0);
a_addr=0;b_addr=0;a_size=0;b_size=1;check(0);
a_size=1;a_space=3;b_space=3;check(0);
$display("V111 RTL directed checks passed: %0d",checks);
$finish;
end
endmodule
