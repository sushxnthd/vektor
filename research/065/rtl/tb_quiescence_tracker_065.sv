`timescale 1ns/1ps
module tb_quiescence_tracker_065;
  reg clk=0;
  always #5 clk=~clk;
  reg rst_n=0, alloc_valid=0, copy_launch=0, copy_terminal=0;
  reg close_tx=0, delivered=0, ack_ready=0;
  reg [7:0] alloc_id=0;
  wire alloc_ready, ack_valid, fault;
  wire [7:0] ack_id;
  quiescence_tracker_065 #(.ID_W(8),.COUNT_W(4)) dut (
    .clk(clk),.rst_n(rst_n),.alloc_valid(alloc_valid),.alloc_ready(alloc_ready),
    .alloc_id(alloc_id),.copy_launch(copy_launch),.copy_terminal(copy_terminal),
    .close_tx(close_tx),.delivered(delivered),.ack_valid(ack_valid),
    .ack_ready(ack_ready),.ack_id(ack_id),.fault(fault)
  );
  task step;
    begin @(posedge clk); #1; @(negedge clk); end
  endtask
  task check;
    input condition;
    input [255:0] msg;
    begin if (!condition) begin $display("FAIL %s",msg); $fatal(1); end end
  endtask
  initial begin
    step(); rst_n=1;
    check(alloc_ready && !ack_valid,"reset idle");
    alloc_valid=1; alloc_id=8'h51; step(); alloc_valid=0;
    check(!alloc_ready,"allocated");
    copy_launch=1; step();
    close_tx=1; step(); copy_launch=0; close_tx=0;
    check(!ack_valid,"two replicas pending");
    copy_terminal=1; delivered=1; step(); delivered=0; copy_terminal=0;
    check(!ack_valid,"one replica still pending");
    step(); step();
    copy_terminal=1; step(); copy_terminal=0;
    check(ack_valid && ack_id==8'h51,"strong ACK only after final terminal");
    repeat (5) begin step(); check(ack_valid && ack_id==8'h51,"stall stability"); end
    ack_ready=1; step(); ack_ready=0;
    check(alloc_ready && !ack_valid,"retired");
    alloc_valid=1; alloc_id=8'h52; step(); alloc_valid=0;
    copy_launch=1; close_tx=1; step(); copy_launch=0; close_tx=0;
    copy_terminal=1; delivered=1; step(); copy_terminal=0; delivered=0;
    check(ack_valid && ack_id==8'h52,"tag recycled after safe drain");
    ack_ready=1; step(); ack_ready=0;
    alloc_valid=1; alloc_id=8'h53; step(); alloc_valid=0;
    close_tx=1; step(); close_tx=0;
    copy_launch=1; step(); copy_launch=0;
    check(fault && !ack_valid,"late launch detected");
    $display("PASS Vektor-065 directed RTL quiescence tracker");
    $finish;
  end
endmodule
