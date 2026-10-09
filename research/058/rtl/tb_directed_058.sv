`timescale 1ns/1ps
module tb_directed_058;
reg clk=0,rst_n=0,push_valid=0,pop_ready=0;
reg [15:0] push_tag=0,push_data=0;
reg [1:0] push_remaining=0;
wire push_ready,pop_valid,pop_urgent;
wire [15:0] pop_tag,pop_data;
wire [1:0] pop_remaining;
wire [2:0] pop_age;
wire [3:0] count;
always #5 clk=~clk;
tagged_return_queue_058 dut(.*);
task drive(input integer v,t,d,r,p);
  begin @(negedge clk); push_valid=v;push_tag=t;push_data=d;
    push_remaining=r;pop_ready=p; #1; end
endtask
initial begin
 #12 rst_n=1;
 drive(1,1,111,3,0); if(count!==0) $fatal(1,"reset");
 drive(1,2,222,1,0); if(count!==1) $fatal(1,"first push");
 drive(0,0,0,0,1); if(count!==2 || pop_tag!==2) $fatal(1,"near-done priority");
 drive(0,0,0,0,1); if(pop_tag!==1 || pop_data!==111) $fatal(1,"tagged payload");
 drive(1,3,333,2,0);
 drive(0,0,0,0,0);
 repeat(70) @(posedge clk);
 drive(0,0,0,0,1);
 if(pop_tag!==3 || pop_age!==4 || !pop_urgent) $fatal(1,"age saturation");
 $display("Vektor-058 directed PASS"); $finish;
end
endmodule
