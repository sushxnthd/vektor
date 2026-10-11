`timescale 1ns/1ps
module tb_return_stable_097;
 parameter integer SOURCES=4,GUARD=16,TAG_BITS=4,IDX_BITS=$clog2(SOURCES);
 reg clk=0;always #5 clk=~clk;
 reg rst_n=0,sink_ready=0;
 reg [SOURCES-1:0] src_valid=0,src_final=0;
 reg [SOURCES*TAG_BITS-1:0] src_tags=0;
 wire [SOURCES-1:0] src_ready;
 wire out_valid,out_final;
 wire [TAG_BITS-1:0] out_tag;
 wire [IDX_BITS-1:0] out_source;
 wb_return_stable_arbiter_097 #(.SOURCES(SOURCES),.TAG_BITS(TAG_BITS),
 .AGE_BITS(10),.GUARD(GUARD)) dut(
 .clk(clk),.rst_n(rst_n),.src_valid(src_valid),.src_final(src_final),
 .src_tags(src_tags),.sink_ready(sink_ready),.src_ready(src_ready),
 .out_valid(out_valid),.out_final(out_final),.out_tag(out_tag),
 .out_source(out_source));
 integer fd,rv,t=0;
 integer iv,fi,ta,rd,ev,ef,et,es,er;
 reg [1023:0] path;
 reg stalled=0,prev_final=0;
 reg [TAG_BITS-1:0] prev_tag=0;
 reg [IDX_BITS-1:0] prev_source=0;
 initial begin
  if(!$value$plusargs("VECTORS=%s",path))$fatal(1,"missing vectors");
  fd=$fopen(path,"r");if(fd==0)$fatal(1,"cannot open %s",path);
  repeat(3)@(negedge clk);rst_n=1;
  while(!$feof(fd))begin
   rv=$fscanf(fd,"%h %h %h %h %h %h %h %h %h\n",
     iv,fi,ta,rd,ev,ef,et,es,er);
   if(rv==9)begin
    @(negedge clk);
    src_valid=iv;src_final=fi;src_tags=ta;sink_ready=rd;
    #1;
    if(out_valid!==ev[0]||out_final!==ef[0]||
       out_tag!==et[TAG_BITS-1:0]||
       out_source!==es[IDX_BITS-1:0]||
       src_ready!==er[SOURCES-1:0])
      $fatal(1,"model mismatch cycle=%0d",t);
    if(stalled&&(!out_valid||out_tag!==prev_tag||
      out_source!==prev_source||out_final!==prev_final))
      $fatal(1,"stalled output changed cycle=%0d",t);
    stalled=out_valid&&!sink_ready;
    prev_tag=out_tag;prev_source=out_source;prev_final=out_final;
    @(posedge clk);#1;t=t+1;
   end else if(!$feof(fd))$fatal(1,"invalid row %0d",t);
  end
  $fclose(fd);
  if(t!=4096)$fatal(1,"expected 4096 vectors got %0d",t);
  $display("PASS RTL 4096 cycles SOURCES=%0d GUARD=%0d",SOURCES,GUARD);
  $finish;
 end
endmodule
