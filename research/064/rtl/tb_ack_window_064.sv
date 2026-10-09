`timescale 1ns/1ps
module tb_ack_window_064;
reg clk=0;always #5 clk=~clk;
reg rst=1,data_valid=0,out_ready=0;
reg [7:0] ack_count=0,free_tags=8,oldest_ack_age=0;
wire out_valid,out_is_ack,data_pop,ack_pop;
wire [2:0] out_ack_count;
ack_window_arbiter_064 #(.TOTAL_TAGS(8),.AGE_ENABLE(1),.AGE_LIMIT(32)) dut(
.clk(clk),.rst(rst),.ack_count(ack_count),.free_tags(free_tags),
.oldest_ack_age(oldest_ack_age),.data_valid(data_valid),.out_ready(out_ready),
.out_valid(out_valid),.out_is_ack(out_is_ack),.out_ack_count(out_ack_count),
.data_pop(data_pop),.ack_pop(ack_pop));
task tick;begin @(posedge clk);#1;end endtask
initial begin
 tick();rst=0;
 @(negedge clk);ack_count=1;free_tags=0;data_valid=1;out_ready=0;
 #1;if(!out_valid||out_is_ack||out_ack_count!=0)$fatal(1,"expected DATA");
 tick();
 @(negedge clk);ack_count=4;free_tags=0;oldest_ack_age=100;
 #1;if(out_is_ack||out_ack_count!=0)$fatal(1,"DATA changed during stall");
 out_ready=1;#1;if(!data_pop||ack_pop)$fatal(1,"DATA handshake");
 tick();
 @(negedge clk);out_ready=0;#1;
 if(!out_is_ack||out_ack_count!=4)$fatal(1,"ACK4 expected");
 tick();
 @(negedge clk);ack_count=7;oldest_ack_age=0;free_tags=8;
 #1;if(!out_is_ack||out_ack_count!=4)$fatal(1,"ACK count changed during stall");
 out_ready=1;#1;if(!ack_pop||data_pop)$fatal(1,"ACK handshake");
 tick();
 @(negedge clk);ack_count=0;data_valid=0;out_ready=0;
 #1;if(out_valid||ack_pop||data_pop)$fatal(1,"idle expected");
 $display("PASS Vektor-064 locked selector");$finish;
end
endmodule
