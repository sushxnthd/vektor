`timescale 1ns/1ps
module tb_wave32_operand_collector;
 localparam WIDTH=1024;
 reg clk=0;
 always #5 clk=~clk;
 reg rst_n=0,enqueue_valid=0,wb_valid=0,dispatch_ready=0;
 reg [7:0] enqueue_tag=0;
 reg [17:0] enqueue_src_regs=0;
 reg [1:0] rf_rsp_valid=0;
 reg [11:0] rf_rsp_reg=0;
 reg [7:0] rf_rsp_bank=0;
 reg [2*WIDTH-1:0] rf_rsp_data=0;
 reg [5:0] wb_reg=0;
 reg [WIDTH-1:0] wb_data=0;
 wire enqueue_ready,dispatch_valid;
 wire [1:0] rf_rsp_accept;
 wire [7:0] dispatch_tag;
 wire [3*WIDTH-1:0] dispatch_operands;
 wire [2:0] captured_debug;
 vektor_wave32_operand_collector dut(
  .clk(clk),.rst_n(rst_n),
  .enqueue_valid(enqueue_valid),.enqueue_ready(enqueue_ready),
  .enqueue_tag(enqueue_tag),.enqueue_src_regs(enqueue_src_regs),
  .rf_rsp_valid(rf_rsp_valid),.rf_rsp_reg(rf_rsp_reg),
  .rf_rsp_bank(rf_rsp_bank),.rf_rsp_data(rf_rsp_data),
  .rf_rsp_accept(rf_rsp_accept),.wb_valid(wb_valid),
  .wb_reg(wb_reg),.wb_data(wb_data),
  .dispatch_valid(dispatch_valid),.dispatch_ready(dispatch_ready),
  .dispatch_tag(dispatch_tag),.dispatch_operands(dispatch_operands),
  .captured_debug(captured_debug)
 );
 reg m_active=0;
 reg [2:0] m_cap=0;
 reg [17:0] m_src=0;
 reg [7:0] m_tag=0;
 reg [3*WIDTH-1:0] m_data=0;
 reg [1:0] exp_accept;
 reg [1:0] eligible;
 reg [2:0] pending;
 reg [2:0] got_rf;
 reg [3*WIDTH-1:0] got_data;
 integer seed=146;
 integer t,i,p,lane,idx,r,completed=0,conflicts=0,bypasses=0,stalls=0,duplicates=0;
 initial begin
  for(t=0;t<1200;t=t+1) begin
   @(negedge clk);
   rst_n=(t!=400 && t!=401);
   r=$random(seed)&32'h7fffffff;
   enqueue_valid=(r%5)!=0;
   enqueue_tag=t & 255;
   for(i=0;i<3;i=i+1) begin
    r=$random(seed)&32'h7fffffff;
    enqueue_src_regs[i*6 +:6]=r%64;
   end
   if((t%3)==0) enqueue_src_regs[6 +:6]=enqueue_src_regs[0 +:6];
   if((t%7)==0) enqueue_src_regs[12 +:6]=enqueue_src_regs[0 +:6];
   r=$random(seed)&32'h7fffffff; dispatch_ready=(r%4)!=0;
   r=$random(seed)&32'h7fffffff; wb_valid=(r%3)==0;
   r=$random(seed)&32'h7fffffff; wb_reg=r%64;
   if(m_active && (t%2)==0) begin
    r=$random(seed)&32'h7fffffff; wb_reg=m_src[(r%3)*6 +:6];
   end
   for(p=0;p<2;p=p+1) begin
    r=$random(seed)&32'h7fffffff; rf_rsp_valid[p]=(r%5)!=0;
    r=$random(seed)&32'h7fffffff; idx=r%3;
    if(m_active && (t%5)!=0)
     rf_rsp_reg[p*6 +:6]=m_src[idx*6 +:6];
    else begin
     r=$random(seed)&32'h7fffffff;
     rf_rsp_reg[p*6 +:6]=r%64;
    end
    rf_rsp_bank[p*4 +:4]=rf_rsp_reg[p*6 +:4];
   end
   for(lane=0;lane<32;lane=lane+1) begin
    rf_rsp_data[lane*32 +:32]=32'h11000000 ^ (t*79+lane);
    rf_rsp_data[WIDTH+lane*32 +:32]=32'h22000000 ^ (t*83+lane);
    wb_data[lane*32 +:32]=32'h33000000 ^ (t*89+lane);
   end
   pending={3{m_active}} & ~m_cap;
   eligible=0;
   for(p=0;p<2;p=p+1) begin
    for(i=0;i<3;i=i+1)
     if(pending[i] && m_src[i*6 +:6]==rf_rsp_reg[p*6 +:6] &&
       !(wb_valid && wb_reg==rf_rsp_reg[p*6 +:6]))
       eligible[p]=rf_rsp_valid[p];
   end
   exp_accept[0]=eligible[0];
   exp_accept[1]=eligible[1] &&
      !(eligible[0] && rf_rsp_bank[0 +:4]==rf_rsp_bank[4 +:4]);
   got_rf=0; got_data=0;
   for(i=0;i<3;i=i+1) begin
    if(pending[i]) begin
     for(p=0;p<2;p=p+1)
      if(exp_accept[p] && m_src[i*6 +:6]==rf_rsp_reg[p*6 +:6]) begin
       got_rf[i]=1;
       got_data[i*WIDTH +:WIDTH]=rf_rsp_data[p*WIDTH +:WIDTH];
      end
    end
   end
   #1;
   if(enqueue_ready !== (!m_active && rst_n)) $fatal(1,"enqueue ready t=%0d",t);
   if(dispatch_valid !== (m_active && (&m_cap) && rst_n)) $fatal(1,"dispatch valid t=%0d",t);
   if(captured_debug !== m_cap) $fatal(1,"captured t=%0d",t);
   if(rst_n && rf_rsp_accept !== exp_accept) $fatal(1,"RF accept t=%0d",t);
   if(dispatch_valid && (dispatch_tag !== m_tag || dispatch_operands !== m_data))
      $fatal(1,"dispatch data/tag t=%0d",t);
   if(dispatch_valid && !dispatch_ready) stalls=stalls+1;
   if(exp_accept[0] && !exp_accept[1] && eligible[1]) conflicts=conflicts+1;
   if(m_active && m_src[0 +:6]==m_src[6 +:6]) duplicates=duplicates+1;
   @(posedge clk);
   if(!rst_n) begin m_active=0; m_cap=0; m_src=0; m_tag=0; m_data=0; end
   else if(!m_active) begin
    if(enqueue_valid) begin
     m_active=1; m_cap=0; m_src=enqueue_src_regs;
     m_tag=enqueue_tag; m_data=0;
    end
   end else if((&m_cap) && dispatch_ready) begin
    m_active=0; m_cap=0; completed=completed+1;
   end else begin
    for(i=0;i<3;i=i+1) if(!m_cap[i]) begin
     if(wb_valid && wb_reg==m_src[i*6 +:6]) begin
      m_cap[i]=1;
      m_data[i*WIDTH +:WIDTH]=wb_data;
      bypasses=bypasses+1;
     end else if(got_rf[i]) begin
      m_cap[i]=1;
      m_data[i*WIDTH +:WIDTH]=got_data[i*WIDTH +:WIDTH];
     end
    end
   end
  end
  if(completed<30 || conflicts<5 || bypasses<10 || stalls<5 || duplicates<10)
    $fatal(1,"coverage completed=%0d conflicts=%0d bypass=%0d stalls=%0d dup=%0d",
           completed,conflicts,bypasses,stalls,duplicates);
  $display("V146 PASS: cycles=1200 completed=%0d conflicts=%0d bypasses=%0d stalls=%0d duplicate_cycles=%0d",
    completed,conflicts,bypasses,stalls,duplicates);
  $finish;
 end
endmodule
