`timescale 1ns/1ps
module tb_kpx_rf_collector;
    reg clk=0;
    always #5 clk=~clk;
    reg rst_n=0, flush_ack=0, instr_valid=0, done_ready=0;
    reg [2:0] src_valid=0;
    reg [11:0] src_addr=0;
    reg [15:0] pending=0;
    wire [1:0] req_valid;
    wire [7:0] req_addr;
    wire [3:0] req_tag;
    wire [31:0] req_txn;
    reg [1:0] rsp_valid=0;
    reg [3:0] rsp_tag=0;
    reg [31:0] rsp_txn=0;
    reg [63:0] rsp_data=0;
    wire flush_wait, instr_ready, done_valid;
    wire [95:0] operands;
    wire [15:0] txn;
    reg [31:0] mem [0:15];
    integer requests=0, cycles=0, i;
    kpx_rf_collector dut (
      .clk(clk), .rst_n(rst_n), .flush_ack_i(flush_ack),
      .flush_wait_o(flush_wait), .instr_valid_i(instr_valid),
      .instr_ready_o(instr_ready), .src_valid_i(src_valid),
      .src_addr_i(src_addr), .rf_pending_i(pending),
      .rf_req_valid_o(req_valid), .rf_req_addr_o(req_addr),
      .rf_req_tag_o(req_tag), .rf_req_txn_o(req_txn),
      .rf_rsp_valid_i(rsp_valid), .rf_rsp_tag_i(rsp_tag),
      .rf_rsp_txn_i(rsp_txn), .rf_rsp_data_i(rsp_data),
      .done_valid_o(done_valid), .done_ready_i(done_ready),
      .operands_o(operands), .txn_o(txn)
    );
    always @(posedge clk) begin
        cycles <= cycles+1;
        if (!rst_n) begin
            rsp_valid <= 0;
        end else begin
            rsp_valid <= req_valid;
            rsp_tag <= req_tag;
            rsp_txn <= req_txn;
            rsp_data[31:0] <= mem[req_addr[3:0]];
            rsp_data[63:32] <= mem[req_addr[7:4]];
            requests <= requests + req_valid[0] + req_valid[1];
            if (req_valid[0] && req_addr[0]) $fatal(1,"bank 0 parity");
            if (req_valid[1] && !req_addr[4]) $fatal(1,"bank 1 parity");
            if ((req_valid[0] && pending[req_addr[3:0]]) ||
                (req_valid[1] && pending[req_addr[7:4]]))
                $fatal(1,"pending register read");
        end
    end
    task reset_and_drain;
      begin
        @(negedge clk); rst_n=0; flush_ack=0;
        repeat(2) @(negedge clk);
        rst_n=1;
        if (!flush_wait) $fatal(1,"must drain after reset");
        repeat(2) @(negedge clk);
        if (instr_ready) $fatal(1,"accepted before flush ack");
        flush_ack=1;
        @(negedge clk); flush_ack=0;
        if (!instr_ready) $fatal(1,"not ready after flush ack");
      end
    endtask
    task send;
      input [2:0] v;
      input [3:0] a0,a1,a2;
      begin
        if (!instr_ready) $fatal(1,"send when busy");
        src_valid=v; src_addr={a2,a1,a0}; instr_valid=1;
        @(negedge clk); instr_valid=0;
      end
    endtask
    task expect_done;
      input [31:0] v0,v1,v2;
      input integer expected_reads;
      integer start_cycle;
      begin
        start_cycle=cycles;
        while (!done_valid && cycles-start_cycle<40) @(negedge clk);
        if (!done_valid) $fatal(1,"timeout");
        if (operands !== {v2,v1,v0})
          $fatal(1,"bad operands got=%h expected=%h",operands,{v2,v1,v0});
        if (requests !== expected_reads)
          $fatal(1,"bad read count %0d != %0d",requests,expected_reads);
        repeat(2) @(negedge clk);
        if (!done_valid || operands !== {v2,v1,v0})
          $fatal(1,"completion did not hold under backpressure");
        done_ready=1;
        @(negedge clk); done_ready=0;
        if (!instr_ready) $fatal(1,"not ready after done");
      end
    endtask
    initial begin
      for(i=0;i<16;i=i+1) mem[i]=32'h100+i;
      reset_and_drain();
      requests=0;
      send(3'b111,4'd0,4'd2,4'd4);
      expect_done(mem[0],mem[2],mem[4],3);
      requests=0;
      send(3'b111,4'd0,4'd0,4'd2);
      expect_done(mem[0],mem[0],mem[2],2);
      requests=0;
      send(3'b111,4'd0,4'd1,4'd2);
      expect_done(mem[0],mem[1],mem[2],3);
      requests=0;
      pending[2]=1;
      send(3'b111,4'd0,4'd2,4'd4);
      repeat(6) @(negedge clk);
      if (done_valid || requests!=2) $fatal(1,"scoreboard hold failed");
      pending[2]=0;
      expect_done(mem[0],mem[2],mem[4],3);
      // HOL discrimination: source 0 blocked, source 1 ready in same bank.
      requests=0;
      pending[0]=1;
      send(3'b011,4'd0,4'd2,4'd0);
      repeat(4) @(negedge clk);
      if (requests!=1 || done_valid) $fatal(1,"HOL bypass failed");
      pending[0]=0;
      expect_done(mem[0],mem[2],0,2);
      requests=0;
      send(3'b000,4'd0,4'd0,4'd0);
      expect_done(0,0,0,0);
      requests=0;
      send(3'b111,4'd0,4'd2,4'd4);
      reset_and_drain();
      requests=0;
      send(3'b111,4'd1,4'd3,4'd5);
      expect_done(mem[1],mem[3],mem[5],3);
      $display("PASS V131 directed RTL collector tests");
      $finish;
    end
    initial begin #50000; $fatal(1,"global timeout"); end
endmodule
