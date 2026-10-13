module tb_close_frontend;
 localparam L=32,W=L*32;
 reg clk=0;always #5 clk=~clk;
 reg rst_n=0,enq=0,ordy=0;
 reg [7:0] tag=0;
 reg [L-1:0] mask=0;
 reg [17:0] src=0;
 reg [1:0] rv=0;
 reg [11:0] rr=0;
 reg [7:0] rb=0;
 reg [2*W-1:0] rd=0;
 wire enq_ready,ov;
 wire [1:0] ra;
 wire [7:0] ot;
 wire [L-1:0] om,support;
 wire [W-1:0] result;
 wire [L*5-1:0] flags;
 integer i,j;
 vektor_wave32_close_frontend dut(
  .clk(clk),.rst_n(rst_n),.enqueue_valid(enq),
  .enqueue_ready(enq_ready),.enqueue_tag(tag),
  .enqueue_mask(mask),.enqueue_src_regs(src),
  .rf_rsp_valid(rv),.rf_rsp_reg(rr),.rf_rsp_bank(rb),
  .rf_rsp_data(rd),.rf_rsp_accept(ra),
  .wb_valid(1'b0),.wb_reg(6'b0),.wb_data({W{1'b0}}),
  .out_valid(ov),.out_ready(ordy),.out_tag(ot),
  .out_mask(om),.out_supported(support),
  .out_result(result),.out_fflags(flags));
 task send(input [7:0] t,input [31:0] cval,input [31:0] expected);
 begin
  @(negedge clk);
  if(!enq_ready) $fatal(1,"collector blocked");
  enq=1;tag=t;mask=32'h00ff00ff;src={6'd33,6'd17,6'd1};
  @(negedge clk);enq=0;rv=2'b11;rr={6'd17,6'd1};rb={4'd1,4'd0};
  for(i=0;i<L;i=i+1) begin
   rd[i*32+:32]=32'h3f800000;
   rd[W+i*32+:32]=32'h3f800000;
  end
  #1;if(ra!==2'b11) $fatal(1,"two RF responses lost");
  @(negedge clk);rv=2'b01;rr={6'd0,6'd33};rb={4'd0,4'd2};
  for(i=0;i<L;i=i+1) rd[i*32+:32]=cval;
  #1;if(ra!==2'b01) $fatal(1,"third RF response lost");
  @(negedge clk);rv=0;
  repeat(5) @(negedge clk);
  if(!ov || ot!==t || om!==32'h00ff00ff || support!==32'h00ff00ff)
   $fatal(1,"frontend valid/tag/mask/support mismatch t=%h ot=%h support=%h",t,ot,support);
  for(j=0;j<L;j=j+1) if(mask[j]) begin
   if(result[j*32+:32]!==expected || flags[j*5+:5]!==0)
    $fatal(1,"frontend result mismatch lane=%0d got=%h expected=%h",j,result[j*32+:32],expected);
  end
  repeat(3) begin
   @(negedge clk);
   if(!ov || ot!==t || support!==32'h00ff00ff) $fatal(1,"frontend stall corrupted");
  end
  ordy=1;
  @(negedge clk);ordy=0;
  if(ov) $fatal(1,"frontend failed to retire");
 end
 endtask
 initial begin
  repeat(3) @(negedge clk);rst_n=1;
  send(8'h49,32'hbf800000,32'h00000000);
  send(8'h9a,32'hbf000000,32'h3f000000);
  $display("V149 PASS: 2 Wave32 collector->multiplier->RNE-close transactions and stalls");
  $finish;
 end
 initial begin #30000;$fatal(1,"timeout");end
endmodule
