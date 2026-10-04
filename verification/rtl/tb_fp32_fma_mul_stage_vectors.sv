`timescale 1ns/1ps
module tb_fp32_fma_mul_stage_vectors;
 reg clk=0,rst_n=0,in_valid=0; reg [31:0] a,b,c;
 wire out_valid,sign_p,sign_c; wire signed [10:0] exp_p,exp_c; wire [47:0] sig_p; wire [23:0] sig_c; wire [2:0] class_a,class_b,class_c;
 reg esp,esc; reg [10:0] eep,eec; reg [47:0] esigp; reg [23:0] esigc; reg [2:0] eca,ecb,ecc;
 integer fd,rc,n=0,errors=0; always #5 clk=~clk; vektor_fp32_fma_mul_stage dut(.*);
 initial begin
  repeat(2) @(negedge clk); rst_n=1; fd=$fopen("verification/fp32/mul_stage_vectors.hex","r"); if(!fd)$fatal(1,"vector file");
  while(!$feof(fd)) begin
   @(negedge clk); rc=$fscanf(fd,"%h %h %h %h %h %h %h %h %h %h %h %h\n",a,b,c,esp,eep,esigp,esc,eec,esigc,eca,ecb,ecc);
   if(rc==12) begin in_valid=1; @(negedge clk); in_valid=0; n=n+1;
    if(!out_valid||sign_p!==esp||exp_p!==eep||sig_p!==esigp||sign_c!==esc||exp_c!==eec||sig_c!==esigc||class_a!==eca||class_b!==ecb||class_c!==ecc) begin
      errors=errors+1; if(errors<10)$display("mismatch n=%0d a=%h b=%h c=%h",n,a,b,c);
    end
   end
  end
  $fclose(fd); if(n<10000)$fatal(1,"too few vectors %0d",n); if(errors)$fatal(1,"%0d/%0d mismatches",errors,n);
  $display("bounded FMA multiply stage vector gate passed: %0d vectors",n); $finish;
 end
endmodule
