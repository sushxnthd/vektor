`timescale 1ns/1ps
module tb_integrated_070;
  reg clk=0; always #5 clk=~clk;
  reg rst_n=0,start=0,fence_ack=0,drop_ack=1;
  wire tx_start_ready,rx_start_ready,tx_data_valid,rx_data_ready;
  wire [1:0] tx_data_uid,rx_ack_uid;
  wire rx_ack_valid,tx_closed,rx_retire,rx_fence_needed;
  wire rx_active,rx_seen,rx_deliver;
  wire [7:0] retries;
  integer deliveries=0,sends=0,retired=0,ack_drops=0;
  wire accepted_ack=rx_ack_valid && !drop_ack;
  reliable_sender_069 #(.UID_W(2),.TIMEOUT_CYCLES(3),.RETRY_W(8)) tx (
    .clk(clk),.rst_n(rst_n),.fabric_quiescent(1'b1),
    .start(start),.start_uid(2'b00),.start_ready(tx_start_ready),
    .data_valid(tx_data_valid),.data_ready(rx_data_ready),
    .data_uid(tx_data_uid),.ack_valid(accepted_ack),.ack_uid(rx_ack_uid),
    .sender_closed(tx_closed),.fabric_retired(rx_retire),.retry_count(retries));
  receiver_dedup_070 #(.UID_W(2)) rx (
    .clk(clk),.rst_n(rst_n),.start(start),.start_uid(2'b00),
    .start_ready(rx_start_ready),.data_valid(tx_data_valid),
    .data_uid(tx_data_uid),.data_ready(rx_data_ready),
    .deliver_valid(rx_deliver),.ack_valid(rx_ack_valid),
    .ack_ready(1'b1),.ack_uid(rx_ack_uid),
    .retire_ok(tx_closed),.retire_valid(rx_retire),.retire_ready(1'b1),
    .fence_ack(fence_ack),.fence_needed(rx_fence_needed),
    .active(rx_active),.seen(rx_seen));
  always @(posedge clk) if(rst_n) begin
    if(rx_deliver) deliveries=deliveries+1;
    if(tx_data_valid && rx_data_ready) sends=sends+1;
    if(rx_ack_valid && drop_ack) ack_drops=ack_drops+1;
    if(rx_retire) retired=retired+1;
  end
  task tick; begin @(posedge clk); #1; end endtask
  integer i,j;
  initial begin
    tick(); rst_n=1;
    for(i=0;i<2;i=i+1) begin
      if(i==1) begin
        if(!rx_fence_needed || rx_start_ready) $fatal(1,"fence missing");
        fence_ack=1; tick(); fence_ack=0;
      end
      if(!tx_start_ready || !rx_start_ready) $fatal(1,"not ready");
      start=1; tick(); start=0;
      drop_ack=1; repeat(3) tick(); drop_ack=0;
      for(j=0;j<30 && retired<=i;j=j+1) tick();
      if(retired!=i+1) $fatal(1,"ACK loss not recovered");
      if(deliveries!=i+1) $fatal(1,"duplicate delivery");
    end
    if(sends<4 || ack_drops<2) $fatal(1,"retry path not exercised");
    $display("PASS integrated retry/dedup/fence sends=%0d",sends);
    $finish;
  end
endmodule
