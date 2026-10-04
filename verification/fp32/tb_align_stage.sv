module tb_fp32_fma_align_stage;
  logic prod_sign,c_sign; logic signed [10:0] prod_exp2,c_exp2;
  logic [47:0] prod_sig; logic [23:0] c_sig;
  logic signed [10:0] common_exp2; logic [55:0] prod_aligned,c_aligned;
  logic prod_sticky,c_sticky,out_prod_sign,out_c_sign;
  integer fd,n,rc,pe,ce,eps,ecs; reg [47:0] pm; reg [23:0] cm; reg [55:0] epa,eca;
  vektor_fp32_fma_align_stage dut(.*);
  initial begin
    fd=$fopen("build/rtl/fp32_align_vectors.txt","r"); if(!fd) $fatal(1,"vectors missing");
    n=0;
    while(!$feof(fd)) begin
      rc=$fscanf(fd,"%d %h %d %h %h %h %d %d\n",pe,pm,ce,cm,epa,eca,eps,ecs);
      if(rc==8) begin
        prod_sign=0; c_sign=1; prod_exp2=pe; prod_sig=pm; c_exp2=ce; c_sig=cm; #1;
        if(prod_aligned!==epa || c_aligned!==eca || prod_sticky!==eps[0] || c_sticky!==ecs[0])
          $fatal(1,"ALIGN mismatch n=%0d pe=%0d ce=%0d got=%h/%h/%b/%b exp=%h/%h/%0d/%0d",n,pe,ce,prod_aligned,c_aligned,prod_sticky,c_sticky,epa,eca,eps,ecs);
        if(common_exp2!==((pe>=ce)?pe:ce)) $fatal(1,"common exponent mismatch");
        n=n+1;
      end
    end
    if(n<20000) $fatal(1,"too few vectors %0d",n);
    $display("FP32_ALIGN_RTL_PASS vectors=%0d",n); $finish;
  end
endmodule
