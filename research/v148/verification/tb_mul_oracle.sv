`timescale 1ns/1ps
module tb_mul_oracle;
 reg clk=0;always #5 clk=~clk;
 reg rst_n=0,iv=0,ordy=0;
 reg [95:0] operands=0;
 wire ir,ov;
 wire [47:0] p;
 wire [10:0] ep,ec;
 wire [23:0] addend;
 wire [0:0] sp,sc;
 wire [8:0] cl;
 wire [7:0] ot;
 wire [0:0] om;
 vektor_wave32_mul_slice #(.LANES(1)) dut(
  .clk(clk),.rst_n(rst_n),.in_valid(iv),.in_ready(ir),
  .in_tag(8'hac),.in_mask(1'b1),.in_operands(operands),
  .out_valid(ov),.out_ready(ordy),.out_tag(ot),.out_mask(om),
  .out_product(p),.out_product_exp(ep),.out_addend(addend),
  .out_addend_exp(ec),.out_product_sign(sp),
  .out_addend_sign(sc),.out_classes(cl)
 );
 integer fd,rc,i,j;
 reg [31:0] a,b,c;
 reg [47:0] want_p;
 reg [10:0] want_ep,want_ec;
 reg [23:0] want_c;
 reg [0:0] want_sp,want_sc;
 reg [8:0] want_cls;
 initial begin
  fd=$fopen("build/v148/mul_vectors.hex","r");
  if(fd==0) $fatal(1,"vectors missing");
  repeat(3) @(negedge clk);rst_n=1;
  for(i=0;i<512;i=i+1) begin
   rc=$fscanf(fd,"%h %h %h %h %h %h %h %h %h %h\n",
    a,b,c,want_p,want_ep,want_c,want_ec,want_sp,want_sc,want_cls);
   if(rc!=10) $fatal(1,"parse error vector %0d rc=%0d",i,rc);
   @(negedge clk);
   if(!ir) $fatal(1,"input blocked unexpectedly");
   operands={c,b,a};iv=1;ordy=0;
   @(negedge clk);iv=0;
   if(ov!==1'b1 || ot!==8'hac || om!==1'b1 ||
      p!==want_p || ep!==want_ep || ec!==want_ec ||
      addend!==want_c || sp!==want_sp || sc!==want_sc ||
      cl!==want_cls)
    $fatal(1,"V148 mismatch vector %0d a=%h b=%h c=%h got product=%h expected=%h",
      i,a,b,c,p,want_p);
   for(j=0;j<(i%4);j=j+1) begin
    @(negedge clk);
    if(!ov || p!==want_p || ep!==want_ep)
      $fatal(1,"backpressure hold mismatch %0d",i);
   end
   ordy=1;
   @(negedge clk);ordy=0;
   if(ov) $fatal(1,"output not retired vector %0d",i);
  end
  $display("V148 PASS: 512 independent special/random stage vectors + elastic holds");
  $finish;
 end
 initial begin #300000;$fatal(1,"timeout");end
endmodule
