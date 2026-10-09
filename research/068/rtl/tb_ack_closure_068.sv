`timescale 1ns/1ps
module tb_ack_closure_068;
 reg clk=0; always #5 clk=~clk;
 reg rst_n=0, fabric_quiescent=0, start=0;
 reg data_send=0, data_clone=0, data_terminal=0, data_deliver=0, data_close=0;
 reg ack_ready=0, ack_clone=0, ack_terminal=0, ack_deliver=0, retire_ready=0;
 wire start_ready, ack_valid, ack_closed, retire_valid, protocol_error;
 wire [3:0] data_pending, ack_pending, ack_queued;
 ack_closure_068 dut(.*);
 task tick; begin @(posedge clk); #1; end endtask
 task clear_inputs; begin
  fabric_quiescent=0; start=0; data_send=0; data_clone=0;
  data_terminal=0; data_deliver=0; data_close=0; ack_ready=0;
  ack_clone=0; ack_terminal=0; ack_deliver=0; retire_ready=0;
 end endtask
 task check(input bit cond, input [255:0] label); begin
  if (!cond) begin $display("FAIL: %s",label); $fatal(1); end
 end endtask
 initial begin
  tick(); rst_n=1; #1;
  check(!start_ready,"reset fence blocks allocation");
  @(negedge clk); fabric_quiescent=1; tick(); clear_inputs();
  check(start_ready,"quiescent fence opens allocation");
  @(negedge clk); start=1; tick(); clear_inputs();
  @(negedge clk); data_send=1; tick(); clear_inputs();
  check(data_pending==1,"DATA copy counted");
  @(negedge clk); data_close=1; tick(); clear_inputs();
  @(negedge clk); data_clone=1; tick(); clear_inputs();
  check(data_pending==2,"in-flight DATA replay counted after sender close");
  @(negedge clk); data_terminal=1; tick(); clear_inputs();
  @(negedge clk); data_terminal=1; data_deliver=1; tick(); clear_inputs();
  check(data_pending==0 && ack_queued==1,"DATA delivery queues ACK");
  @(negedge clk); ack_ready=1; tick(); clear_inputs();
  check(ack_pending==1 && ack_queued==0,"ACK admitted to network");
  tick(); check(ack_closed,"ACK producer closes with ACK still in flight");
  @(negedge clk); ack_clone=1; tick(); clear_inputs();
  check(ack_pending==2,"in-flight ACK replay after producer closure");
  @(negedge clk); ack_terminal=1; tick(); clear_inputs();
  @(negedge clk); ack_terminal=1; ack_deliver=1; tick(); clear_inputs();
  check(!protocol_error,"late ACK after producer closure is legal");
  check(retire_valid && ack_pending==0,"retirement only after ACK extinction");
  @(negedge clk); retire_ready=1; tick(); clear_inputs();
  check(start_ready,"slot reusable after retirement");
  $display("PASS Vektor-068 directed RTL closure/replay/reset fence"); $finish;
 end
endmodule
