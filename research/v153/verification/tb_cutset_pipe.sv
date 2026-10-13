// V153 differential test: frozen V151 24,220-vector corpus, elastic stalls, tags/masks.
module tb_cutset_pipe;
 reg clk=0,rst_n=0,in_valid=0,out_ready=0;
 always #5 clk=~clk;
 reg [7:0] in_tag=0;
 reg [0:0] in_mask=0;
 reg [47:0] product=0;
 reg [10:0] product_exp=0,addend_exp=0;
 reg [23:0] addend=0;
 reg product_sign=0,addend_sign=0;
 reg [8:0] classes=0;
 wire in_ready,out_valid;
 wire [7:0] out_tag;
 wire [0:0] out_mask;
 wire [31:0] out_result;
 wire [4:0] out_fflags;
 wire [31:0] ref_result;
 wire [4:0] ref_flags;
 vektor_fp32_bounded_tail ref_fma(
  .product_sign(product_sign),.addend_sign(addend_sign),
  .product_exp(product_exp),.addend_exp(addend_exp),
  .product(product),.addend(addend),.classes(classes),
  .result(ref_result),.fflags(ref_flags));
 vektor_wave32_cutset_pipe #(.LANES(1)) dut(
  .clk(clk),.rst_n(rst_n),.in_valid(in_valid),.in_ready(in_ready),
  .in_tag(in_tag),.in_mask(in_mask),
  .in_product(product),.in_product_exp(product_exp),
  .in_addend(addend),.in_addend_exp(addend_exp),
  .in_product_sign(product_sign),.in_addend_sign(addend_sign),
  .in_classes(classes),.out_valid(out_valid),.out_ready(out_ready),
  .out_tag(out_tag),.out_mask(out_mask),
  .out_result(out_result),.out_fflags(out_fflags));
 reg [31:0] expected_result=0;
 reg [4:0] expected_flags=0;
 reg [31:0] q_result [0:25000];
 reg [4:0] q_flags [0:25000];
 reg [7:0] q_tag [0:25000];
 reg q_mask [0:25000];
 integer fd,status,ps,cs,pe,ce;
 integer issued=0,head=0,tail=0,cycle=0;
 reg accepted=0,done=0;
 initial begin
  fd=$fopen("build/v151/full_vectors.txt","r");
  if(fd==0) $fatal(1,"missing frozen corpus");
  repeat(3) @(negedge clk);
  rst_n=1;
 end
 always @(negedge clk) if(rst_n) begin
  cycle=cycle+1;
  out_ready=(cycle%13<9);
  if(accepted || !in_valid) begin
   accepted=0;
   if(!done) begin
    status=$fscanf(fd,"%d %d %d %d %h %h %h %h %h\n",
      ps,cs,pe,ce,product,addend,classes,expected_result,expected_flags);
    if(status==9) begin
     in_valid=1;product_sign=ps;addend_sign=cs;
     product_exp=pe;addend_exp=ce;
     in_tag=issued[7:0];in_mask=issued[0];
     issued=issued+1;
    end else begin in_valid=0;done=1;end
   end else in_valid=0;
  end
  if(cycle>150000) $fatal(1,"watchdog %0d/%0d",head,tail);
 end
 always @(posedge clk) if(rst_n) begin
  accepted=0;
  if(out_valid&&out_ready) begin
   if(head>=tail) $fatal(1,"unexpected output");
   if(out_result!==q_result[head]||out_fflags!==q_flags[head]||
      out_tag!==q_tag[head]||out_mask!==q_mask[head])
    $fatal(1,"output mismatch idx=%0d got=%h/%h exp=%h/%h tag=%h/%h",
      head,out_result,out_fflags,q_result[head],q_flags[head],out_tag,q_tag[head]);
   head=head+1;
  end
  if(in_valid&&in_ready) begin
   if(ref_result!==expected_result||ref_flags!==expected_flags)
    $fatal(1,"reference/oracle mismatch idx=%0d got=%h/%h exp=%h/%h",
      tail,ref_result,ref_flags,expected_result,expected_flags);
   q_result[tail]=expected_result;q_flags[tail]=expected_flags;
   q_tag[tail]=in_tag;q_mask[tail]=in_mask;
   tail=tail+1;accepted=1;
  end
  if(head==24220) begin
   if(tail!=24220) $fatal(1,"not all issued");
   $display("V153 PASS: 24220 exact vectors, elastic tag/mask retirement, cycles=%0d",cycle);
   $finish;
  end
 end
endmodule
