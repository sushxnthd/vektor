module tb_tag_compare;
  reg valid;
  reg [7:0] rtag, stag;
  wire base_match, isolated_match;
  integer a,b,v;
  v238_tag_match_baseline u_base(.valid(valid),.return_tag(rtag),.slot_tag(stag),.match_o(base_match));
  v238_tag_match_isolated u_iso(.valid(valid),.return_tag(rtag),.slot_tag(stag),.match_o(isolated_match));
  initial begin
    for (v=0;v<2;v=v+1)
      for (a=0;a<256;a=a+1)
        for (b=0;b<256;b=b+1) begin
          valid=v; rtag=a; stag=b; #1;
          if (base_match !== isolated_match) $fatal(1,"Mismatch v=%d r=%d s=%d",v,a,b);
        end
    $display("V238 RTL equivalence PASS 131072");
    $finish;
  end
endmodule
