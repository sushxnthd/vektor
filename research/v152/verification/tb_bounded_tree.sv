module tb_bounded_tree;
 reg ps=0,cs=0; reg signed [10:0] pe=0,ce=0;
 reg [47:0] pm=0; reg [23:0] cm=0; reg [8:0] classes=0;
 wire [31:0] original,balanced; wire [4:0] original_flags,balanced_flags;
 reg [31:0] expected; reg [4:0] expected_flags;
 integer fd,rc,n,ipe,ice;
 vektor_fp32_bounded_tail ref_dut(.product_sign(ps),.addend_sign(cs),.product_exp(pe),.addend_exp(ce),.product(pm),.addend(cm),.classes(classes),.result(original),.fflags(original_flags));
 vektor_fp32_bounded_tree candidate(.product_sign(ps),.addend_sign(cs),.product_exp(pe),.addend_exp(ce),.product(pm),.addend(cm),.classes(classes),.result(balanced),.fflags(balanced_flags));
 initial begin
  fd=$fopen("build/v151/full_vectors.txt","r");
  if(!fd) $fatal(1,"missing frozen corpus");
  n=0;
  while(!$feof(fd)) begin
   rc=$fscanf(fd,"%h %h %d %d %h %h %h %h %h\n",ps,cs,ipe,ice,pm,cm,classes,expected,expected_flags);
   if(rc==9) begin
    pe=ipe; ce=ice; #1;
    if(balanced!==expected || balanced_flags!==expected_flags || balanced!==original || balanced_flags!==original_flags)
     $fatal(1,"V152 mismatch %0d balanced=%h/%h ref=%h/%h expected=%h/%h",n,balanced,balanced_flags,original,original_flags,expected,expected_flags);
    n=n+1;
   end
  end
  $fclose(fd);
  if(n<16916) $fatal(1,"insufficient corpus: %0d",n);
  $display("V152 PASS: %0d differential and oracle vectors",n);
  $finish;
 end
endmodule
