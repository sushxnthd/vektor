`timescale 1ns/1ps
module tb_integrated_071;
 reg clk=0; always #5 clk=~clk;
 reg rst_n=0,start=0, data_drop=0, ack_drop=0, ack_stall=0;
 reg data_stall=0,external_inflight=0;
 wire tx_start_ready,rx_start_ready,tx_data_valid,tx_data_ready;
 wire [1:0] tx_data_uid,rx_ack_uid,router_data_uid,router_ack_uid;
 wire rx_ack_valid,rx_ack_ready,tx_closed,rx_retire,rx_fence_needed;
 wire rx_active,rx_seen,rx_deliver,router_data_valid,router_ack_valid;
 wire rx_data_ready,quiescent;
 wire [2:0] dc,ac;
 wire [7:0] retries;
 reg fence_token=0;
 integer delivered=0, retired=0, accepted_data=0, accepted_ack=0;
 wire can_start=!rx_active && !rx_fence_needed && dc==0 && ac==0 && !external_inflight;
 reliable_sender_069 #(.UID_W(2),.TIMEOUT_CYCLES(4),.RETRY_W(8)) tx (
   .clk(clk),.rst_n(rst_n),.fabric_quiescent(can_start),
   .start(start),.start_uid(2'b00),.start_ready(tx_start_ready),
   .data_valid(tx_data_valid),.data_ready(tx_data_ready),
   .data_uid(tx_data_uid),.ack_valid(router_ack_valid),
   .ack_uid(router_ack_uid),.sender_closed(tx_closed),
   .fabric_retired(quiescent),.retry_count(retries));
 receiver_dedup_070 #(.UID_W(2)) rx (
   .clk(clk),.rst_n(rst_n),.start(start),.start_uid(2'b00),
   .start_ready(rx_start_ready),.data_valid(router_data_valid),
   .data_uid(router_data_uid),.data_ready(rx_data_ready),
   .deliver_valid(rx_deliver),.ack_valid(rx_ack_valid),
   .ack_ready(rx_ack_ready),.ack_uid(rx_ack_uid),
   .retire_ok(quiescent),.retire_valid(rx_retire),
   .retire_ready(1'b1),.fence_ack(fence_token),
   .fence_needed(rx_fence_needed),.active(rx_active),.seen(rx_seen));
 bounded_fabric_071 #(.UID_W(2),.DEPTH(4)) fabric (
   .clk(clk),.rst_n(rst_n),
   .data_in_valid(tx_data_valid),.data_in_ready(tx_data_ready),
   .data_in_uid(tx_data_uid),.data_clone(1'b1),
   .data_out_valid(router_data_valid),.data_out_ready(rx_data_ready),
   .data_out_uid(router_data_uid),.data_drop(data_drop),
   .data_stall(data_stall),
   .ack_in_valid(rx_ack_valid),.ack_in_ready(rx_ack_ready),
   .ack_in_uid(rx_ack_uid),.ack_clone(1'b1),
   .ack_out_valid(router_ack_valid),.ack_out_ready(1'b1),
   .ack_out_uid(router_ack_uid),.ack_drop(ack_drop),
   .ack_stall(ack_stall),.producer_closed(tx_closed),
   .external_inflight(external_inflight),.quiescent(quiescent),
   .data_occupancy(dc),.ack_occupancy(ac));
 always @(posedge clk or negedge rst_n) begin
   if(!rst_n) fence_token<=0;
   else if(start) fence_token<=0;
   else if(quiescent) fence_token<=1;
 end
 always @(posedge clk) if(rst_n) begin
   if(rx_deliver) delivered=delivered+1;
   if(rx_retire) retired=retired+1;
   if(tx_data_valid && tx_data_ready) accepted_data=accepted_data+1;
   if(router_ack_valid) accepted_ack=accepted_ack+1;
   if(quiescent && (dc!=0 || ac!=0 || external_inflight))
     $fatal(1,"false quiescence");
 end
 task tick; begin @(posedge clk); #1; end endtask
 integer i,j;
 initial begin
   tick(); rst_n=1;
   for(i=0;i<2;i=i+1) begin
     if(!tx_start_ready || !rx_start_ready) $fatal(1,"reuse blocked incorrectly");
     start=1; tick(); start=0;
     ack_drop=1; data_drop=0;
     repeat(3) tick();
     ack_drop=0; ack_stall=1;
     repeat(3) tick();
     if(quiescent) $fatal(1,"premature quiescence while ACK stalled");
     ack_stall=0;
     for(j=0;j<80 && retired<=i;j=j+1) tick();
     if(retired!=i+1 || delivered!=i+1)
       $fatal(1,"end-to-end liveness/exactly-once failure");
     repeat(3) tick();
     if(rx_fence_needed) $fatal(1,"fence token not consumed");
   end
   if(accepted_data<2 || accepted_ack<2) $fatal(1,"traffic not exercised");
   $display("PASS Vektor-071 integrated bounded router: deliveries=%0d data_admits=%0d ack_deliveries=%0d",delivered,accepted_data,accepted_ack);
   $finish;
 end
endmodule
