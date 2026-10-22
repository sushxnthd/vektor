
`timescale 1ns/1ps
module tb_v277;
reg clk=0; always #5 clk=~clk;
reg rst=1,req_valid=0,invalidate=0;
reg [7:0] req_tag=0,inv_tag=0;
wire [31:0] rf_data={24'b0,req_tag}^32'h12345678;
wire ha,hb,ra,rb;
wire [31:0] da,db;
integer seed=277,i,ma=0,mb=0;
v277_operand_cache #(.CONFIDENCE(1)) a(clk,rst,req_valid,req_tag,rf_data,invalidate,inv_tag,ha,ra,da);
v277_operand_cache #(.CONFIDENCE(0)) b(clk,rst,req_valid,req_tag,rf_data,invalidate,inv_tag,hb,rb,db);
initial begin
 @(negedge clk);rst=0;
 for(i=0;i<50000;i=i+1) begin
  @(negedge clk);
  req_valid=$unsigned($random(seed))%5!=0;
  req_tag=$unsigned($random(seed))%16;
  invalidate=$unsigned($random(seed))%17==0;
  inv_tag=$unsigned($random(seed))%16;
  #1;
  if(req_valid && (da!==rf_data || db!==rf_data))$fatal(1,"data mismatch %0d",i);
  if(ha!==(req_valid&&!ra) || hb!==(req_valid&&!rb))$fatal(1,"hit/miss mismatch %0d",i);
  if(ra)ma=ma+1;
  if(rb)mb=mb+1;
 end
 $display("V277 PASS 50000 functional checks candidate_reads=%0d baseline_reads=%0d",ma,mb);
 $finish;
end
endmodule
