`timescale 1ns/1ps
module tb_fp32_fma_mul_stage_random;
 reg clk=0,rst_n=0,in_valid=0; reg [31:0] a,b,c; wire out_valid,sign_p,sign_c;
 wire signed [10:0] exp_p,exp_c; wire [47:0] sig_p; wire [23:0] sig_c; wire [2:0] class_a,class_b,class_c;
 integer i,errors=0; reg [31:0] s=32'h5eed1234;
 always #5 clk=~clk; vektor_fp32_fma_mul_stage dut(.*);
 function [31:0] nxt(input [31:0] x); nxt={x[30:0],x[31]^x[21]^x[1]^x[0]}; endfunction
 function [23:0] esig(input [31:0] x); esig=(x[30:23]==0)?{1'b0,x[22:0]}:{1'b1,x[22:0]}; endfunction
 function signed [10:0] eexp(input [31:0] x); begin if(x[30:23]==0)eexp=-11'sd149; else eexp=$signed({3'b000,x[30:23]})-11'sd150; end endfunction
 function [2:0] ecls(input [31:0] x); begin if(x[30:23]==8'hff)ecls=(x[22:0]==0)?3'b010:(x[22]?3'b011:3'b100); else if((x[30:23]==0)&&(x[22:0]==0))ecls=3'b000; else ecls=3'b001; end endfunction
 task check; reg [47:0] ep; reg signed [10:0] ee; begin
   ep=esig(a)*esig(b); ee=eexp(a)+eexp(b);
   if(!out_valid||sign_p!==(a[31]^b[31])||sig_p!==ep||exp_p!==ee||sign_c!==c[31]||sig_c!==esig(c)||exp_c!==eexp(c)||class_a!==ecls(a)||class_b!==ecls(b)||class_c!==ecls(c)) begin errors=errors+1; if(errors<8)$display("mismatch i=%0d a=%h b=%h c=%h",i,a,b,c); end
 end endtask
 initial begin a=0;b=0;c=0; repeat(2)@(negedge clk); rst_n=1;
   for(i=0;i<20000;i=i+1) begin s=nxt(s);a=s;s=nxt(s);b=s;s=nxt(s);c=s; @(negedge clk);in_valid=1; @(posedge clk);#1; check; in_valid=0; end
   if(errors)$fatal(1,"%0d mismatches",errors); $display("FP32-MUL-RTL-004 PASS: 20000 deterministic tuples"); $finish; end
endmodule
