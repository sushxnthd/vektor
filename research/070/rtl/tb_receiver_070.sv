`timescale 1ns/1ps
module tb_receiver_070;
  reg clk=0; always #5 clk=~clk;
  reg rst_n=0, start=0, data_valid=0, ack_ready=0;
  reg retire_ok=0, retire_ready=1, fence_ack=0;
  reg [1:0] start_uid=0, data_uid=0;
  wire start_ready,data_ready,deliver_valid,ack_valid,retire_valid;
  wire fence_needed,active,seen;
  wire [1:0] ack_uid;
  integer deliveries=0,acks=0;
  receiver_dedup_070 #(.UID_W(2)) dut (
    .clk(clk),.rst_n(rst_n),.start(start),.start_uid(start_uid),
    .start_ready(start_ready),.data_valid(data_valid),.data_uid(data_uid),
    .data_ready(data_ready),.deliver_valid(deliver_valid),
    .ack_valid(ack_valid),.ack_ready(ack_ready),.ack_uid(ack_uid),
    .retire_ok(retire_ok),.retire_valid(retire_valid),
    .retire_ready(retire_ready),.fence_ack(fence_ack),
    .fence_needed(fence_needed),.active(active),.seen(seen));
  always @(posedge clk) if(rst_n) begin
    if(deliver_valid) deliveries=deliveries+1;
    if(ack_valid && ack_ready) acks=acks+1;
  end
  task tick; begin @(posedge clk); #1; end endtask
  initial begin
    tick(); rst_n=1; start=1;
    tick(); start=0;
    if(!active || start_ready) $fatal(1,"start failed");
    data_valid=1;
    #1; if(!deliver_valid) $fatal(1,"first DATA not delivered");
    tick(); data_valid=0;
    if(deliveries!=1 || !ack_valid) $fatal(1,"first DATA not ACKed");
    data_valid=1;
    #1; if(deliver_valid) $fatal(1,"duplicate delivered");
    tick(); data_valid=0;
    ack_ready=1; tick(); ack_ready=0;
    if(acks!=1 || ack_valid) $fatal(1,"ACK handshake failed");
    retire_ok=1;
    #1; if(!retire_valid) $fatal(1,"retirement missing");
    tick(); retire_ok=0;
    if(!fence_needed || start_ready) $fatal(1,"UID reused before fence");
    data_valid=1; start=1;
    #1; if(data_ready || deliver_valid) $fatal(1,"stale DATA consumed");
    tick(); data_valid=0; start=0;
    if(active || start_ready) $fatal(1,"fence bypass");
    fence_ack=1; tick(); fence_ack=0;
    if(!start_ready) $fatal(1,"fence not accepted");
    start=1; tick(); start=0;
    data_valid=1;
    #1; if(!deliver_valid) $fatal(1,"fresh reused UID dropped");
    tick(); data_valid=0;
    if(deliveries!=2) $fatal(1,"wrong logical delivery count");
    $display("PASS receiver dedup and forced UID reuse");
    $finish;
  end
endmodule
