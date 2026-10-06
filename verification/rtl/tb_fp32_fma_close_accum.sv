module tb_fp32_fma_close_accum;
  logic ps, cs; logic signed [10:0] pe, ce; logic [47:0] pm; logic [23:0] cm;
  logic close, ss, z; logic signed [10:0] base; logic [48:0] sm;
  integer fd, rc, n; integer ipe, ice; reg [48:0] esm; reg ess, ez;
  vektor_fp32_fma_close_accum dut(.prod_sign(ps),.c_sign(cs),.prod_lsb_exp(pe),.c_lsb_exp(ce),
    .prod_sig(pm),.c_sig(cm),.close_path(close),.common_lsb_exp(base),.sum_sign(ss),.sum_mag(sm),.exact_zero(z));
  initial begin
    fd=$fopen("build/rtl/close_vectors.txt","r"); if (!fd) $fatal(1,"missing close vectors");
    n=0;
    while (!$feof(fd)) begin
      rc=$fscanf(fd,"%h %h %d %d %h %h %h %h %h\n",ps,cs,ipe,ice,pm,cm,ess,ez,esm);
      if (rc==9) begin
        pe=ipe; ce=ice; #1; n=n+1;
        if (!close || ss!==ess || z!==ez || sm!==esm) begin
          $display("FAIL n=%0d pe=%0d ce=%0d pm=%h cm=%h close=%b got=%h exp=%h sign=%b/%b zero=%b/%b",
            n,ipe,ice,pm,cm,close,sm,esm,ss,ess,z,ez); $fatal;
        end
      end
    end
    $fclose(fd);
    if (n<20000) $fatal(1,"insufficient vectors %0d",n);
    $display("PASS close accumulator %0d real-FP32 cancellation vectors",n); $finish;
  end
endmodule
