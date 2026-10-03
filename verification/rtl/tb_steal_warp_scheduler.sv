`timescale 1ns/1ps

module tb_steal_warp_scheduler;
    logic clk = 1'b0;
    logic rst_n = 1'b0;
    logic [31:0] wave_valid;
    logic [31:0] wave_ready;
    logic [3:0] issue_accept;
    logic [3:0] issue_valid;
    logic [4:0] issue_wave0;
    logic [4:0] issue_wave1;
    logic [4:0] issue_wave2;
    logic [4:0] issue_wave3;

    vektor_steal_warp_scheduler dut (
        .clk(clk), .rst_n(rst_n),
        .wave_valid(wave_valid), .wave_ready(wave_ready),
        .issue_accept(issue_accept),
        .issue_valid(issue_valid),
        .issue_wave0(issue_wave0), .issue_wave1(issue_wave1),
        .issue_wave2(issue_wave2), .issue_wave3(issue_wave3)
    );

    always #5 clk = ~clk;

    task reset_dut;
        begin
            rst_n = 1'b0;
            issue_accept = 4'b1111;
            repeat (2) @(posedge clk);
            rst_n = 1'b1;
            #1;
        end
    endtask

    initial begin
        wave_valid = '0;
        wave_ready = '0;
        issue_accept = 4'b1111;
        reset_dut();

        // Balanced: one ready wave per partition, same as fixed scheduler.
        wave_valid = '0;
        wave_valid[0] = 1'b1;
        wave_valid[8] = 1'b1;
        wave_valid[16] = 1'b1;
        wave_valid[24] = 1'b1;
        wave_ready = wave_valid;
        #1;
        if (issue_valid !== 4'b1111)
            $fatal(1, "balanced case should propose four, got %b", issue_valid);

        // Backpressure invariant: proposals that are not accepted must retry.
        reset_dut();
        wave_valid = '0;
        wave_valid[0] = 1'b1;
        wave_valid[1] = 1'b1;
        wave_valid[2] = 1'b1;
        wave_ready = wave_valid;
        issue_accept = 4'b0000;
        #1;
        if (issue_valid[1:0] !== 2'b11 || issue_wave0 !== 5'd0 || issue_wave1 !== 5'd1)
            $fatal(1, "unexpected initial proposals %b %0d %0d", issue_valid, issue_wave0, issue_wave1);
        @(posedge clk);
        #1;
        if (issue_wave0 !== 5'd0 || issue_wave1 !== 5'd1)
            $fatal(1, "unaccepted proposals advanced scheduler state");

        // Accept only wave 0; blocked wave 1 must become the next primary.
        issue_accept = 4'b0001;
        @(posedge clk);
        #1;
        if (issue_wave0 !== 5'd1 || issue_wave1 !== 5'd2)
            $fatal(1, "partial acceptance lost retry: got %0d %0d", issue_wave0, issue_wave1);

        // A concentrated partition exposes primary + one backup, doubling the
        // fixed scheduler's one-issue behavior without a full global arbiter.
        reset_dut();
        wave_valid = '0;
        wave_valid[8] = 1'b1;
        wave_valid[9] = 1'b1;
        wave_valid[10] = 1'b1;
        wave_valid[11] = 1'b1;
        wave_ready = wave_valid;
        issue_accept = 4'b1111;
        #1;
        if (issue_valid !== 4'b0011)
            $fatal(1, "single donor partition should propose two, got %b", issue_valid);

        // Two concentrated partitions each expose a backup, filling all slots.
        reset_dut();
        wave_valid = '0;
        wave_valid[0] = 1'b1;
        wave_valid[1] = 1'b1;
        wave_valid[2] = 1'b1;
        wave_valid[3] = 1'b1;
        wave_valid[8] = 1'b1;
        wave_valid[9] = 1'b1;
        wave_valid[10] = 1'b1;
        wave_valid[11] = 1'b1;
        wave_ready = wave_valid;
        #1;
        if (issue_valid !== 4'b1111)
            $fatal(1, "two donor partitions should fill four slots, got %b", issue_valid);

        // Sparse readiness remains sparse; the stealing mechanism invents no work.
        reset_dut();
        wave_valid = '0;
        wave_valid[3] = 1'b1;
        wave_valid[21] = 1'b1;
        wave_ready = wave_valid;
        #1;
        if (issue_valid !== 4'b0101)
            $fatal(1, "sparse case expected 0101, got %b", issue_valid);

        $display("steal warp scheduler tests passed");
        $finish;
    end
endmodule
