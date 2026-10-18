`timescale 1ns/1ps
module tb_rf_exchange_202;
  reg [3:0] request_valid;
  reg [15:0] src0_bank_flat,src1_bank_flat;
  reg [1:0] priority_turn;
  wire [3:0] grant,greedy_grant;
  integer t,m,i,b,c,ng,ne,opportunities,errors;
  reg [3:0] candidate;
  reg valid;
  vektor_rf_exchange_arbiter dut (
    .request_valid(request_valid),.src0_bank_flat(src0_bank_flat),
    .src1_bank_flat(src1_bank_flat),.priority_turn(priority_turn),
    .grant(grant),.greedy_grant(greedy_grant));
  function integer pop4;
    input [3:0] x;
    begin pop4=x[0]+x[1]+x[2]+x[3]; end
  endfunction
  function legal;
    input [3:0] x;
    input [15:0] a,bb;
    integer bank,slot,count;
    begin
      legal=1;
      for(bank=0;bank<16;bank=bank+1) begin
        count=0;
        for(slot=0;slot<4;slot=slot+1) if(x[slot]) begin
          if(a[4*slot +:4]==bank) count=count+1;
          if(bb[4*slot +:4]==bank) count=count+1;
        end
        if(count>2) legal=0;
      end
    end
  endfunction
  initial begin
    errors=0; opportunities=0;
    // Deterministic full 4-bank input sweep; 4^8=65536 cases.
    for(t=0;t<65536;t=t+1) begin
      request_valid=4'b1111; priority_turn=t[1:0];
      for(i=0;i<4;i=i+1) begin
        src0_bank_flat[i*4 +:4]=(t>>(4*i))&3;
        src1_bank_flat[i*4 +:4]=(t>>(4*i+2))&3;
      end
      #1;
      ng=pop4(greedy_grant); ne=pop4(grant);
      if(!legal(grant,src0_bank_flat,src1_bank_flat) || ne<ng) begin
        errors=errors+1;
        if(errors<5) $display("FAIL t=%0d greedy=%b exchange=%b",t,greedy_grant,grant);
      end
      for(m=0;m<16;m=m+1) begin
        candidate=m[3:0];
        if(legal(candidate,src0_bank_flat,src1_bank_flat) && pop4(candidate)>ne) begin
          errors=errors+1;
          if(errors<5) $display("NOT OPTIMAL t=%0d candidate=%b exchange=%b",t,candidate,grant);
        end
      end
      if(ne>ng) opportunities=opportunities+1;
    end
    $display("V202 exhaustive cases=65536 opportunities=%0d errors=%0d",opportunities,errors);
    if(errors!=0) $fatal(1,"V202 exact cardinality failure");
    $finish;
  end
endmodule
