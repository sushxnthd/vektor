module tb_fp32_fma_close_accum;
  logic ps, cs; logic signed [10:0] pe, ce; logic [47:0] pm; logic [23:0] cm;
  logic close, ss, z; logic signed [10:0] base; logic [48:0] sm;
  vektor_fp32_fma_close_accum dut(.prod_sign(ps),.c_sign(cs),.prod_lsb_exp(pe),.c_lsb_exp(ce),
    .prod_sig(pm),.c_sig(cm),.close_path(close),.common_lsb_exp(base),.sum_sign(ss),.sum_mag(sm),.exact_zero(z));
  task check(input logic ips, ics, input integer ipe, ice, input logic [47:0] ipm, input logic [23:0] icm,
             input logic eclose, ess, ez, input logic [48:0] esm);
    begin ps=ips;cs=ics;pe=ipe;ce=ice;pm=ipm;cm=icm; #1;
      if (close!==eclose || (eclose && (ss!==ess || z!==ez || sm!==esm))) begin
        $display("FAIL d=%0d close=%b sign=%b zero=%b mag=%h",ipe-ice,close,ss,z,sm); $fatal;
      end
    end
  endtask
  initial begin
    check(0,1,0,0,48'h000000800000,24'h800000,1,0,1,49'h0);
    check(0,1,1,0,48'h000000800000,24'h800000,1,0,0,49'h0800000);
    check(1,0,0,1,48'h000000800000,24'h800000,1,0,0,49'h0800000);
    check(0,0,0,0,48'hffffffffffff,24'hffffff,1,0,0,49'h10000fffffe);
    check(0,1,2,0,48'h800000,24'h800000,0,0,0,49'h0);
    $display("PASS close accumulator directed tests"); $finish;
  end
endmodule
