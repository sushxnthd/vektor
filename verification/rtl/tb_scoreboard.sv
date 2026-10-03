`timescale 1ns/1ps
module tb_scoreboard;
    logic clk=0, rst_n=0;
    logic [31:0] wave_valid, wave_ready;
    logic [191:0] src0_flat, src1_flat;
    logic [3:0] issue_valid, issue_writes_dst, wb_valid;
    logic [19:0] issue_wave_flat, wb_wave_flat;
    logic [23:0] issue_dst_flat, wb_dst_flat;

    vektor_scoreboard dut(.*);
    always #5 clk=~clk;

    task set_src(input integer w, input [5:0] a, input [5:0] b);
      begin src0_flat[w*6 +:6]=a; src1_flat[w*6 +:6]=b; end
    endtask

    initial begin
      wave_valid='0; src0_flat='0; src1_flat='0;
      issue_valid='0; issue_writes_dst='0; issue_wave_flat='0; issue_dst_flat='0;
      wb_valid='0; wb_wave_flat='0; wb_dst_flat='0;
      #2; rst_n=0; #8; rst_n=1;
      wave_valid[0]=1; set_src(0,6'd1,6'd2); #1;
      if (!wave_ready[0]) $fatal(1,"clean wave must be ready");

      issue_valid[0]=1; issue_writes_dst[0]=1;
      issue_wave_flat[4:0]=0; issue_dst_flat[5:0]=6'd7;
      @(posedge clk); #1;
      issue_valid='0; issue_writes_dst='0;
      set_src(0,6'd7,6'd2); #1;
      if (wave_ready[0]) $fatal(1,"RAW dependency was not blocked");

      wb_valid[0]=1; wb_wave_flat[4:0]=0; wb_dst_flat[5:0]=6'd7;
      @(posedge clk); #1; wb_valid='0; #1;
      if (!wave_ready[0]) $fatal(1,"writeback did not release dependency");

      // Dependencies are per-wave: wave 1 may read r7 while wave 0 owns r7.
      issue_valid[0]=1; issue_writes_dst[0]=1;
      issue_wave_flat[4:0]=0; issue_dst_flat[5:0]=6'd7;
      @(posedge clk); #1; issue_valid='0; issue_writes_dst='0;
      wave_valid[1]=1; set_src(1,6'd7,6'd3); #1;
      if (!wave_ready[1]) $fatal(1,"scoreboard leaked dependency across waves");

      // Same-cycle retire+reissue to same register must leave it pending.
      wb_valid[0]=1; wb_wave_flat[4:0]=0; wb_dst_flat[5:0]=6'd7;
      issue_valid[0]=1; issue_writes_dst[0]=1;
      issue_wave_flat[4:0]=0; issue_dst_flat[5:0]=6'd7;
      @(posedge clk); #1; wb_valid='0; issue_valid='0; issue_writes_dst='0;
      set_src(0,6'd7,6'd2); #1;
      if (wave_ready[0]) $fatal(1,"same-cycle reissue lost pending state");

      $display("scoreboard tests passed");
      $finish;
    end
endmodule
