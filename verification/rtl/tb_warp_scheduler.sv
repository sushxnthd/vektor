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

        check_issue4(0, 1, 2, 3);
        @(posedge clk);
        check_issue4(4, 5, 6, 7);

        wave_valid[8] = 1'b0;
        wave_ready[9] = 1'b0;
        @(posedge clk);
        check_issue4(10, 11, 12, 13);

        wave_valid = '0;
        wave_ready = '0;
        wave_valid[3] = 1'b1;
        wave_valid[21] = 1'b1;
        wave_ready[3] = 1'b1;
        wave_ready[21] = 1'b1;
        @(posedge clk);
        #1;
        if (issue_valid !== 4'b0011)
            $fatal(1, "expected two valid issues, got %b", issue_valid);
        if (issue_wave0 == issue_wave1)
            $fatal(1, "scheduler issued duplicate wave id");
        if (!((issue_wave0 == 21 && issue_wave1 == 3) ||
              (issue_wave0 == 3 && issue_wave1 == 21)))
            $fatal(1, "unexpected sparse issue ids %0d %0d", issue_wave0, issue_wave1);

        $display("warp scheduler tests passed");
        $finish;
    end
endmodule
