`timescale 1ns/1ps
module tb;
  reg clk=0; always #5 clk=~clk;
  reg rst=1, req_valid=0, retire_valid=0;
  reg [15:0] req_key=0, retire_key=0;
  reg [1:0] retire_slot=0;
  wire idx_ready,idx_merge,idx_new,cam_ready,cam_merge,cam_new;
  wire [1:0] idx_grant,cam_grant;
  wire [3:0] idx_occ,cam_occ,idx_waiters,cam_waiters;
  wire idx_ret,cam_ret;
  v275_tlb_join #(.INDEXED(1)) idx(.clk(clk),.rst(rst),.req_valid(req_valid),.req_key(req_key),
    .retire_valid(retire_valid),.retire_slot(retire_slot),.retire_key(retire_key),
    .retire_match(idx_ret),.retire_waiters(idx_waiters),.req_ready(idx_ready),
    .merged(idx_merge),.new_walk(idx_new),.grant_slot(idx_grant),.occupied(idx_occ));
  v275_tlb_join #(.INDEXED(0)) cam(.clk(clk),.rst(rst),.req_valid(req_valid),.req_key(req_key),
    .retire_valid(retire_valid),.retire_slot(retire_slot),.retire_key(retire_key),
    .retire_match(cam_ret),.retire_waiters(cam_waiters),.req_ready(cam_ready),
    .merged(cam_merge),.new_walk(cam_new),.grant_slot(cam_grant),.occupied(cam_occ));
  task drive_req(input [15:0] k);
    begin @(negedge clk);req_valid=1;req_key=k;retire_valid=0;#1; end
  endtask
  task drive_ret(input [1:0] slot,input [15:0] k);
    begin @(negedge clk);req_valid=0;retire_valid=1;retire_slot=slot;retire_key=k;#1; end
  endtask
  task check(input cond,input [255:0] label);
    begin if(!cond)begin $display("FAIL: %0s",label);$fatal(1);end end
  endtask
  integer i;
  initial begin
    repeat(2) @(negedge clk);rst=0;
    drive_req(16'h0000);
    check(idx_new&&cam_new&&idx_ready&&cam_ready,"first allocation");
    @(posedge clk);#1;
    drive_req(16'h0002);
    check(idx_new&&cam_new,"second allocation");
    @(posedge clk);#1;
    drive_req(16'h0004);
    check(!idx_ready&&cam_new,"same-set collision only indexed");
    @(posedge clk);#1;
    drive_req(16'h0000);
    check(idx_merge&&cam_merge,"duplicate page merge");
    @(posedge clk);#1;
    drive_ret(2'd0,16'hffff);
    check(!idx_ret&&!cam_ret,"stale response rejected");
    @(posedge clk);#1;
    drive_ret(2'd0,16'h0000);
    check(idx_ret&&cam_ret&&idx_waiters==2&&cam_waiters==2,"waiter broadcast count");
    @(posedge clk);#1;
    drive_req(16'h0004);
    check(idx_new&&cam_merge,"set collision resolves after retire");
    @(posedge clk);#1;
    for(i=0;i<100;i=i+1)begin
      drive_req(i[15:0]);
      check(!(idx_new&&idx_merge)&&!(cam_new&&cam_merge),"mutually exclusive grant");
      if(idx_ready)check(idx_new||idx_merge,"indexed ready means accepted");
      if(cam_ready)check(cam_new||cam_merge,"cam ready means accepted");
      @(posedge clk);#1;
    end
    $display("PASS V275 directed and 100 random-like admission checks");$finish;
  end
endmodule
