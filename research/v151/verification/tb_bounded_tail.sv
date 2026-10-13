module tb_bounded_tail;
 reg ps=0,cs=0;reg signed [10:0] pe=0,ce=0;
 reg [47:0] pm=0;reg [23:0] cm=0;reg [8:0] classes=0;
 wire [31:0] result;wire [4:0] fflags;
 reg [31:0] expected;reg [4:0] flags_expected;
 integer fd,rc,n,ipe,ice;
 vektor_fp32_bounded_tail dut(
  .product_sign(ps),.addend_sign(cs),.product_exp(pe),.addend_exp(ce),
  .product(pm),.addend(cm),.classes(classes),.result(result),.fflags(fflags));
 initial begin
  fd=$fopen("build/v151/full_vectors.txt","r");
  if(!fd) $fatal(1,"missing exact reference vectors");
  n=0;
  while(!$feof(fd)) begin
   rc=$fscanf(fd,"%h %h %d %d %h %h %h %h %h\n",ps,cs,ipe,ice,pm,cm,classes,expected,flags_expected);
   if(rc==9) begin
    pe=ipe;ce=ice;#1;
    if(result!==expected || fflags!==flags_expected)
     $fatal(1,"V151 FAIL vector=%0d got=%h/%h expected=%h/%h p=%h pe=%0d c=%h ce=%0d cls=%h",n,result,fflags,expected,flags_expected,pm,ipe,cm,ice,classes);
    n=n+1;
   end
  end
  $fclose(fd);
  if(n<16916) $fatal(1,"wrong vector count %0d",n);
  $display("V151 PASS: %0d full-range FP32 FMA reference vectors",n);
  $finish;
 end
endmodule
