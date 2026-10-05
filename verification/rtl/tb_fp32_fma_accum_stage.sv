module tb_fp32_fma_accum_stage;
  logic ps,cs; logic [55:0] p,c; logic ss; logic [56:0] m; logic z;
  integer i; logic [56:0] expm; logic exps;
  vektor_fp32_fma_accum_stage dut(.prod_sign(ps),.c_sign(cs),.prod_aligned(p),.c_aligned(c),.sum_sign(ss),.sum_mag(m),.exact_zero(z));
  task check; begin
    #1;
    if(ps==cs) begin expm={1'b0,p}+{1'b0,c}; exps=ps; end
    else if(p>c) begin expm={1'b0,p}-{1'b0,c}; exps=ps; end
    else if(c>p) begin expm={1'b0,c}-{1'b0,p}; exps=cs; end
    else begin expm=0; exps=0; end
    if(m!==expm || ss!==exps || z!==(expm==0)) $fatal(1,"ACCUM mismatch");
  end endtask
  initial begin
    p=56'hffffffffffffff; c=56'hffffffffffffff; ps=0; cs=0; check();
    p=56'h80000000000000; c=56'h7fffffffffffff; ps=0; cs=1; check();
    p=56'h7fffffffffffff; c=56'h80000000000000; ps=0; cs=1; check();
    p=56'h123456789abcde; c=p; ps=0; cs=1; check();
    for(i=0;i<10000;i=i+1) begin
      p={$urandom,$urandom}; c={$urandom,$urandom}; ps=$urandom; cs=$urandom; check();
    end
    $display("FP32_ACCUM_RTL_PASS vectors=10004"); $finish;
  end
endmodule
