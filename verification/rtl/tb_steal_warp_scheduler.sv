`timescale 1ns/1ps

module tb_steal_warp_scheduler;
    logic clk = 1'b0;
    logic rst_n = 1'b0;
    logic [31:0] wave_valid;
    logic [31:0] wave_ready;
    logic [3:0] issue_valid;
    logic [4:0] issue_wave0;
    logic [4:0] issue_wave1;
    logic [4:0] issue_wave2;
    logic [4:0] issue_wave3;

    vektor_steal_warp_scheduler dut (
        .clk(clk), .rst_n(rst_n),
        .wave_valid(wave_valid), .wave_ready(wave_ready),
        .issue_valid(issue_valid),
        .issue_wave0(issue_wave0), .issue_wave1(issue_wave1),
        .issue_wave2(issue_wave2), .issue_wave3(issue_wave3)
    );

    always #5 clk = ~clk;

    initial begin
        wave_valid = '0;
        wave_ready = '0;
        #2 rst_n = 1'b0;
        #8 rst_n = 1'b1;

        // Balanced: one ready wave per partition, same as fixed scheduler.
        wave_valid[0] = 1'b1;
        wave_valid[8] = 1'b1;
        wave_valid[16] = 1'b1;
        wave_valid[24] = 1'b1;
        wave_ready = wave_valid;
        #1;
        if (issue_valid !== 4'b1111)
            $fatal(1, "balanced case should issue four, got %b", issue_valid);

        // One concentrated partition exposes a primary + one backup, doubling
        // the fixed scheduler's one-issue behavior without a full global arbiter.
        wave_valid = '0;
        wave_ready = '0;
        wave_valid[8] = 1'b1;
        wave_valid[9] = 1'b1;
        wave_valid[10] = 1'b1;
        wave_valid[11] = 1'b1;
        wave_ready = wave_valid;
        #1;
        if (issue_valid !== 4'b0011)
            $fatal(1, "single donor partition should issue two, got %b", issue_valid);
        if (issue_wave0 !== 5'd9 || issue_wave1 !== 5'd8)
            $fatal(1, "unexpected primary/steal waves %0d %0d", issue_wave0, issue_wave1);

        // Two concentrated partitions each expose a backup, filling all slots.
        wave_valid = '0;
        wave_ready = '0;
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
        wave_valid = '0;
        wave_ready = '0;
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
