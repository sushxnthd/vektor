`timescale 1ns/1ps
module tb_rf_equiv_085b;
  reg [7:0] rv;
  reg [15:0] rb;
  reg [3:0] wv;
  reg [7:0] wb;
  wire [7:0] rg0,rg1;
  wire [3:0] wg0,wg1;
  integer seed,i;
  rf_shared_arbiter_085 old_dut(.rd_valid(rv),.rd_bank(rb),.wr_valid(wv),.wr_bank(wb),.rd_grant(rg0),.wr_grant(wg0));
  rf_shared_arbiter_085b new_dut(.rd_valid(rv),.rd_bank(rb),.wr_valid(wv),.wr_bank(wb),.rd_grant(rg1),.wr_grant(wg1));
  initial begin
    seed=850085;
    for(i=0;i<10000;i=i+1) begin
      rv=$random(seed);rb=$random(seed);wv=$random(seed);wb=$random(seed);
      #1;
      if(rg0 !== rg1 || wg0 !== wg1) $fatal(1,"grant mismatch %0d",i);
    end
    $display("PASS 10000 deterministic equivalence vectors");
    $finish;
  end
endmodule
