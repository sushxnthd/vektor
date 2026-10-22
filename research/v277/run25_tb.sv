// combinational RF model only; synchronous macro timing is not verified
`timescale 1ns/1ps
module tb_v277_run25;
reg clk=0; always #5 clk=~clk;
reg rst=1,req_valid=0,invalidate=0;
reg [7:0] req_tag=0,inv_tag=0;
wire [31:0] rf_data={24'b0,req_tag}^32'h13579bdf;
wire h2,h1,r2,r1; wire [31:0] d2,d1;
integer i,seed=27725,n2=0,n1=0;
v277_operand_cache #(.CONFIDENCE(1)) dut(clk,rst,req_valid,req_tag,rf_data,invalidate,inv_tag,h2,r2,d2);
v277_onebit control(clk,rst,req_valid,req_tag,rf_data,invalidate,inv_tag,h1,r1,d1);
initial begin
 @(negedge clk);rst=0;
 for(i=0;i<50000;i=i+1) begin
  @(negedge clk);
  req_valid=($unsigned($random(seed))%5)!=0;
  req_tag=$unsigned($random(seed))%16;
  invalidate=($unsigned($random(seed))%17)==0;
  inv_tag=$unsigned($random(seed))%16;
  #1;
  if(req_valid && (d2!==rf_data || d1!==rf_data))$fatal(1,"data mismatch %0d",i);
  if(h2!==(req_valid&&!r2) || h1!==(req_valid&&!r1))$fatal(1,"hit mismatch %0d",i);
  if(r2)n2=n2+1; if(r1)n1=n1+1;
 end
 $display("PASS 50000 v277_misses=%0d onebit_misses=%0d",n2,n1);
 $finish;
end
endmodule
