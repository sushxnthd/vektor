module tb_close_round;
 reg ps=0,cs=0;
 reg signed [10:0] pe=0,ce=0;
 reg [47:0] pm=0;
 reg [23:0] cm=0;
 wire supported;
 wire [31:0] result;
 wire [4:0] fflags;
 reg [31:0] expected;
 reg [4:0] flags_expected;
 integer fd,rc,n,ipe,ice;
 vektor_fp32_close_round dut(
  .product_sign(ps),.addend_sign(cs),.product_exp(pe),.addend_exp(ce),
  .product(pm),.addend(cm),.classes(9'b001001001),
  .supported(supported),.result(result),.fflags(fflags));
 initial begin
  fd=$fopen("build/v149/close_vectors.txt","r");
  if(!fd) $fatal(1,"missing independent oracle vectors");
  n=0;
  while(!$feof(fd)) begin
   rc=$fscanf(fd,"%h %h %d %d %h %h %h %h\n",ps,cs,ipe,ice,pm,cm,expected,flags_expected);
   if(rc==8) begin
    pe=ipe;ce=ice;#1;
    if(supported!==1'b1 || result!==expected || fflags!==flags_expected)
     $fatal(1,"V149 FAIL vector=%0d got=%h/%h expected=%h/%h support=%b",n,result,fflags,expected,flags_expected,supported);
    n=n+1;
   end
  end
  $fclose(fd);
  if(n!=3072) $fatal(1,"wrong vector count %0d",n);
  $display("V149 PASS: %0d libc-crosschecked close-path RNE vectors",n);
  $finish;
 end
endmodule
