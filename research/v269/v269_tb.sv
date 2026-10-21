`timescale 1ns/1ps
module v269_tb;
 reg clk=0;always #5 clk=~clk;
 reg rst_n=0,in_valid=0,in_class=0,ready_slow=1,ready_fast=1,out_ready=1;
 reg [31:0] in_data=0;
 wire in_ready,out_valid,out_class;
 wire [31:0] out_data;
`ifdef CONTROL2
 v269_ready_select_control #(.DEPTH(2)) dut(.*);
`elsif CONTROL8
 v269_ready_select_control #(.DEPTH(8)) dut(.*);
`else
 v269_split_response_fifo dut(.*);
`endif
 reg [31:0] expected0[0:20000],expected1[0:20000];
 integer wr0=0,wr1=0,rd0=0,rd1=0,offered=0,accepted=0,delivered=0;
 integer t=0,phase=0,seed=32'h13579bdf,rnd;
 initial begin
   repeat(3) @(negedge clk);rst_n=1;
   for(phase=0;phase<3;phase=phase+1)
     for(t=0;t<3000;t=t+1) begin
       @(negedge clk);
       rnd=$random(seed);
       in_valid=(rnd&16'hff)<215;
       in_class=((rnd>>8)&16'hff)<160;
       in_data=(phase<<24)|offered;
       ready_slow=(phase==0)?1'b1:((phase==1)?(t%20>=16):(t%13>=7));
       ready_fast=(phase==2)?(t%19>=3):1'b1;
       out_ready=(phase==2)?(t%7!=0):1'b1;
       @(posedge clk);
       if(out_valid&&out_ready) begin
         if(!out_class) begin
           if(rd0>=wr0||out_data!==expected0[rd0]) $fatal(1,"slow order/data mismatch");
           rd0=rd0+1;
         end else begin
           if(rd1>=wr1||out_data!==expected1[rd1]) $fatal(1,"fast order/data mismatch");
           rd1=rd1+1;
         end
         delivered=delivered+1;
       end
       if(in_valid&&in_ready) begin
         if(!in_class) begin expected0[wr0]=in_data;wr0=wr0+1;end
         else begin expected1[wr1]=in_data;wr1=wr1+1;end
         accepted=accepted+1;
       end
       if(in_valid) offered=offered+1;
     end
   for(t=0;t<50;t=t+1) begin
     @(negedge clk);in_valid=0;ready_slow=1;ready_fast=1;out_ready=1;
     @(posedge clk);
     if(out_valid&&out_ready) begin
       if(!out_class) begin
         if(rd0>=wr0||out_data!==expected0[rd0]) $fatal(1,"drain slow mismatch");
         rd0=rd0+1;
       end else begin
         if(rd1>=wr1||out_data!==expected1[rd1]) $fatal(1,"drain fast mismatch");
         rd1=rd1+1;
       end
       delivered=delivered+1;
     end
   end
   if(rd0!=wr0||rd1!=wr1) $fatal(1,"undelivered entries");
   $display("PASS V269 RTL: offered=%0d accepted=%0d delivered=%0d slow=%0d fast=%0d",offered,accepted,delivered,rd0,rd1);
   $finish;
 end
endmodule
