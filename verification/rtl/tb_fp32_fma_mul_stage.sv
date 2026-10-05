`timescale 1ns/1ps
module tb_fp32_fma_mul_stage;
 reg clk=0,rst_n=0,in_valid=0; reg [31:0] a,b,c;
 wire out_valid,sign_p,sign_c; wire signed [10:0] exp_p,exp_c;
 wire [47:0] sig_p; wire [23:0] sig_c; wire [2:0] class_a,class_b,class_c;
 always #5 clk=~clk;
 vektor_fp32_fma_mul_stage dut(.*);
 task drive(input [31:0] aa,input [31:0] bb,input [31:0] cc);
  begin @(negedge clk); in_valid=1;a=aa;b=bb;c=cc; @(negedge clk); in_valid=0; end
 endtask
 initial begin
  a=0;b=0;c=0; repeat(2) @(negedge clk); rst_n=1;
  drive(32'h3fc00000,32'h40000000,32'h3f800000);
  if(!out_valid||sig_p!==48'hc00000000000||exp_p!==-46||sig_c!==24'h800000||exp_c!==-23)
   $fatal(1,"normal unpack/multiply mismatch p=%h ep=%0d c=%h ec=%0d",sig_p,exp_p,sig_c,exp_c);
  drive(32'h00000001,32'h3f800000,32'h80000000);
  if(class_a!==3'b001||class_c!==3'b000||sig_p!==48'h000000800000||exp_p!==-172||sign_c!==1'b1)
   $fatal(1,"subnormal/zero classification mismatch");
  drive(32'h7f800000,32'h00000000,32'h7f800001);
  if(class_a!==3'b010||class_b!==3'b000||class_c!==3'b100) $fatal(1,"special classification mismatch");
  drive(32'h7f7fffff,32'hff7fffff,32'h00800000);
  if(sign_p!==1'b1||sig_p!==48'hfffffe000001||exp_p!==208||sig_c!==24'h800000||exp_c!==-149)
   $fatal(1,"max-finite product contract mismatch");
  drive(32'h7fc00001,32'h3f800000,32'h7f800000);
  if(class_a!==3'b011||class_b!==3'b001||class_c!==3'b010)
   $fatal(1,"qNaN/finite/inf classification mismatch");
  $display("bounded FMA multiply stage tests passed"); $finish;
 end
endmodule
