`timescale 1ns/1ps
module tb_ack_uid_guard_066;
 reg clk=0; always #5 clk=~clk;
 reg rst_n=0, alloc_valid=0, ack_in_valid=0, closed_quiescent=0;
 reg retire_ready=0;
 reg [1:0] alloc_tag=0, ack_in_tag=0;
 reg [7:0] alloc_uid=0, ack_in_uid=0;
 wire alloc_ready, ack_in_ready, retire_valid, stale_ack_pulse, accepted_ack_pulse;
 wire [1:0] retire_tag;
 wire [7:0] retire_uid;
 ack_uid_guard_066 #(.TAG_W(2),.UID_W(8)) dut(
 .clk(clk),.rst_n(rst_n),.alloc_valid(alloc_valid),.alloc_ready(alloc_ready),
 .alloc_tag(alloc_tag),.alloc_uid(alloc_uid),.ack_in_valid(ack_in_valid),
 .ack_in_ready(ack_in_ready),.ack_in_tag(ack_in_tag),.ack_in_uid(ack_in_uid),
 .closed_quiescent(closed_quiescent),.retire_valid(retire_valid),
 .retire_ready(retire_ready),.retire_tag(retire_tag),.retire_uid(retire_uid),
 .stale_ack_pulse(stale_ack_pulse),.accepted_ack_pulse(accepted_ack_pulse));
 task step; begin @(posedge clk); #1; end endtask
 task expect_retire(input bit expected); begin
   if(retire_valid !== expected) $fatal(1,"retire mismatch");
 end endtask
 initial begin
 step; rst_n=1;
 @(negedge clk); alloc_valid=1; alloc_tag=0; alloc_uid=8'h11;
 step; alloc_valid=0;
 @(negedge clk); ack_in_valid=1; ack_in_tag=0; ack_in_uid=8'h11;
 if(!accepted_ack_pulse) $fatal(1,"A ACK rejected");
 step; ack_in_valid=0; expect_retire(0);
 @(negedge clk); closed_quiescent=1;
 step; closed_quiescent=0; expect_retire(1);
 if(retire_uid !== 8'h11) $fatal(1,"A UID");
 @(negedge clk); retire_ready=1;
 step; retire_ready=0; expect_retire(0);
 @(negedge clk); alloc_valid=1; alloc_tag=0; alloc_uid=8'h12;
 step; alloc_valid=0;
 @(negedge clk); ack_in_valid=1; ack_in_tag=0; ack_in_uid=8'h11;
 if(!stale_ack_pulse || accepted_ack_pulse) $fatal(1,"old replay accepted");
 step; ack_in_valid=0; expect_retire(0);
 @(negedge clk); ack_in_valid=1; ack_in_uid=8'h12;
 if(!accepted_ack_pulse) $fatal(1,"B ACK rejected");
 step; ack_in_valid=0; expect_retire(0);
 @(negedge clk); closed_quiescent=1;
 step; closed_quiescent=0; expect_retire(1);
 repeat(4) begin
   step; expect_retire(1);
   if(retire_uid !== 8'h12) $fatal(1,"unstable retirement");
 end
 @(negedge clk); retire_ready=1;
 step; expect_retire(0);
 $display("PASS Vektor-066 replay and retirement"); $finish;
 end
endmodule
