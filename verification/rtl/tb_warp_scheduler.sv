`timescale 1ns/1ps

module tb_warp_scheduler;
    logic clk = 1'b0;
    logic rst_n = 1'b0;
    logic [31:0] wave_valid;
    logic [31:0] wave_ready;
    logic [3:0] issue_valid;
    logic [4:0] issue_wave0;
    logic [4:0] issue_wave1;
    logic [4:0] issue_wave2;
    logic [4:0] issue_wave3;

    vektor_warp_scheduler dut (
        .clk(clk),
        .rst_n(rst_n),
        .wave_valid(wave_valid),
        .wave_ready(wave_ready),
        .issue_valid(issue_valid),
        .issue_wave0(issue_wave0),
        .issue_wave1(issue_wave1),
        .issue_wave2(issue_wave2),
        .issue_wave3(issue_wave3)
    );

    always #5 clk = ~clk;

    task check_issue4(
        input [4:0] a,
        input [4:0] b,
        input [4:0] c,
        input [4:0] d
    );
        begin
            #1;
            if (issue_valid !== 4'b1111)
                $fatal(1, "expected four valid issues, got %b", issue_valid);
            if (issue_wave0 !== a || issue_wave1 !== b ||
                issue_wave2 !== c || issue_wave3 !== d)
                $fatal(1, "unexpected issue ids %0d %0d %0d %0d",
                       issue_wave0, issue_wave1, issue_wave2, issue_wave3);
        end
    endtask

    initial begin
        wave_valid = 32'hffff_ffff;
        wave_ready = 32'hffff_ffff;

        #2;
        rst_n = 1'b0;
        #8;
        rst_n = 1'b1;

        // One issue from each 8-wave scheduler partition.
        check_issue4(0, 8, 16, 24);
        @(posedge clk);
        check_issue4(1, 9, 17, 25);

        // Each partition skips its own unavailable waves independently.
        wave_valid[2] = 1'b0;
        wave_ready[10] = 1'b0;
        @(posedge clk);
        check_issue4(3, 11, 18, 26);

        // Sparse-ready case: only partitions 0 and 2 can issue.
        wave_valid = '0;
        wave_ready = '0;
        wave_valid[3] = 1'b1;
        wave_valid[21] = 1'b1;
        wave_ready[3] = 1'b1;
        wave_ready[21] = 1'b1;
        @(posedge clk);
        #1;
        if (issue_valid !== 4'b0101)
            $fatal(1, "expected partition-valid mask 0101, got %b", issue_valid);
        if (issue_wave0 !== 5'd3 || issue_wave2 !== 5'd21)
            $fatal(1, "unexpected sparse issue ids %0d %0d", issue_wave0, issue_wave2);

        $display("warp scheduler tests passed");
        $finish;
    end
endmodule
