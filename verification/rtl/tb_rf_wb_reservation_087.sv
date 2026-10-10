`timescale 1ns/1ps
module tb_rf_wb_reservation_087 #(
  parameter integer BANKS=4, BANK_W=2, REQS=4, LAT_W=3,
  MAX_LATENCY=4, WB_PORTS_PER_BANK=1,
  COUNT_W=(WB_PORTS_PER_BANK>1) ? $clog2(WB_PORTS_PER_BANK+1) : 1,
  CYCLES=4096
);
  reg clk=0;
  always #5 clk=~clk;
  reg rst_n=0;
  reg [REQS-1:0] req_valid=0;
  reg [REQS*BANK_W-1:0] req_bank=0;
  reg [REQS*LAT_W-1:0] req_latency=0;
  wire [REQS-1:0] req_grant;
  wire [BANKS*COUNT_W-1:0] due_count;
  integer fd, rc, idx, rst_i, v_i, b_i, l_i, g_i, d_i;
  reg [REQS-1:0] expected_grants;
  reg [BANKS*COUNT_W-1:0] expected_due;
  reg [1023:0] vector_path;
  rf_wb_reservation_087 #(.BANKS(BANKS),.BANK_W(BANK_W),.REQS(REQS),
      .LAT_W(LAT_W),.MAX_LATENCY(MAX_LATENCY),
      .WB_PORTS_PER_BANK(WB_PORTS_PER_BANK)) dut(
      .clk(clk), .rst_n(rst_n), .req_valid(req_valid),
      .req_bank(req_bank), .req_latency(req_latency),
      .req_grant(req_grant), .due_count(due_count));
  initial begin
    if(!$value$plusargs("VEC=%s",vector_path)) $fatal(1,"Missing +VEC=path");
    fd=$fopen(vector_path,"r");
    if(fd==0) $fatal(1,"Missing generated test vectors: %0s",vector_path);
    for(idx=0;idx<CYCLES;idx=idx+1) begin
      @(negedge clk);
      rc=$fscanf(fd,"%d %x %x %x %x %x\n",rst_i,v_i,b_i,l_i,g_i,d_i);
      if(rc!=6) $fatal(1,"Bad vector %0d rc=%0d",idx,rc);
      rst_n=rst_i[0]; req_valid=v_i; req_bank=b_i;
      req_latency=l_i; expected_grants=g_i; expected_due=d_i;
      #1;
      if(req_grant !== expected_grants || due_count !== expected_due)
        $fatal(1,"Mismatch cycle %0d grant=%h/%h due=%h/%h",idx,
               req_grant,expected_grants,due_count,expected_due);
    end
    $fclose(fd);
    $display("PASS Vektor-087: %0d oracle-matched cycles, ports=%0d",CYCLES,WB_PORTS_PER_BANK);
    $finish;
  end
endmodule
