`timescale 1ns/1ps
module tb_fence_egress_063;
  reg clk=0; always #5 clk=~clk;
  reg rst=1;
  reg data_valid=0,ack_valid=0,out_ready=0;
  reg [7:0] data_tag=0,ack_tag=0;
  wire data_ready,ack_ready,out_valid,out_is_ack;
  wire [7:0] out_tag;
  fence_egress_arbiter_063 #(.TAGW(8),.ACK_FIRST(1)) dut(
    .clk(clk),.rst(rst),.data_valid(data_valid),.data_ready(data_ready),
    .data_tag(data_tag),.ack_valid(ack_valid),.ack_ready(ack_ready),
    .ack_tag(ack_tag),.out_valid(out_valid),.out_ready(out_ready),
    .out_is_ack(out_is_ack),.out_tag(out_tag));
  integer t,ds=0,as=0,outs=0;
  reg stalled=0, prev_ack=0;
  reg fire_data=0,fire_ack=0;
  reg [7:0] prev_tag=0;
  reg [31:0] rng=32'h1badf00d;
  function [31:0] next_rng(input [31:0] x);
    begin next_rng=(x ^ (x<<13)); next_rng=next_rng^(next_rng>>17);
      next_rng=next_rng^(next_rng<<5); end
  endfunction
  initial begin
    repeat(3) @(negedge clk);
    rst=0;
    for(t=0;t<12000;t=t+1) begin
      @(negedge clk);
      rng=next_rng(rng);
      out_ready=(rng[4:2]!=3'b000);
      if(!data_valid) begin data_valid=rng[0]; data_tag=rng[15:8]; end
      if(!ack_valid) begin ack_valid=rng[1]; ack_tag=rng[23:16]; end
      #1;
      if(stalled && (!out_valid || out_is_ack!=prev_ack || out_tag!=prev_tag))
        $fatal(1,"output changed under backpressure at cycle %0d",t);
      if(data_ready && ack_ready)$fatal(1,"dual issue on one lane");
      if(out_valid && out_ready) begin
        outs=outs+1;
        if(out_is_ack) begin
          if(!ack_valid || out_tag!=ack_tag)$fatal(1,"ACK identity mismatch");
          as=as+1;
        end else begin
          if(!data_valid || out_tag!=data_tag)$fatal(1,"DATA identity mismatch");
          ds=ds+1;
        end
      end
      fire_data=data_ready; fire_ack=ack_ready;
      stalled=out_valid && !out_ready;
      prev_ack=out_is_ack; prev_tag=out_tag;
      @(posedge clk);
      #1;
      if(fire_ack) ack_valid=0;
      if(fire_data) data_valid=0;
    end
    if(outs!=ds+as || ds<100 || as<100)$fatal(1,"conservation/fairness");
    $display("PASS Vektor-063 arbiter cycles=%0d data=%0d ack=%0d",t,ds,as);
    $finish;
  end
endmodule
