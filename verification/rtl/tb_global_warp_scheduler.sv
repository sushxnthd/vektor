`timescale 1ns/1ps

module tb_global_warp_scheduler;
    logic clk = 1'b0;
    logic rst_n = 1'b0;
    logic [31:0] wave_valid;
    logic [31:0] wave_ready;
    logic [3:0] issue_valid;
    logic [4:0] issue_wave0;
    logic [4:0] issue_wave1;
    logic [4:0] issue_wave2;
    logic [4:0] issue_wave3;

    vektor_global_warp_scheduler dut (
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

    task expect4(input [4:0] a, input [4:0] b, input [4:0] c, input [4:0] d);
        begin
            #1;
            if (issue_valid !== 4'b1111)
                $fatal(1, "expected four issues, got %b", issue_valid);
            if (issue_wave0 !== a || issue_wave1 !== b || issue_wave2 !== c || issue_wave3 !== d)
                $fatal(1, "unexpected waves %0d %0d %0d %0d", issue_wave0, issue_wave1, issue_wave2, issue_wave3);
        end
    endtask

    initial begin
        wave_valid = '0;
        wave_ready = '0;

        #2;
        rst_n = 1'b0;
        #8;
        rst_n = 1'b1;

        // Full-ready case starts from wave 0 and advances round-robin by four.
        wave_valid = 32'hffff_ffff;
        wave_ready = 32'hffff_ffff;
        expect4(0, 1, 2, 3);
        @(posedge clk);
        expect4(4, 5, 6, 7);

        // Clustered readiness: unlike the fixed 4x8 scheduler, four waves in
        // one former partition can all consume the four-wide issue capacity.
        wave_valid = '0;
        wave_ready = '0;
        wave_valid[8] = 1'b1;
        wave_valid[9] = 1'b1;
        wave_valid[10] = 1'b1;
        wave_valid[11] = 1'b1;
        wave_ready = wave_valid;
        @(posedge clk);
        #1;
        if (issue_valid !== 4'b1111)
            $fatal(1, "clustered ready set should issue four, got %b", issue_valid);
        if (issue_wave0 !== 5'd8 || issue_wave1 !== 5'd9 || issue_wave2 !== 5'd10 || issue_wave3 !== 5'd11)
            $fatal(1, "unexpected clustered order %0d %0d %0d %0d", issue_wave0, issue_wave1, issue_wave2, issue_wave3);

        // Sparse case issues only the ready waves and preserves circular order.
        wave_valid = '0;
        wave_ready = '0;
        wave_valid[3] = 1'b1;
        wave_valid[21] = 1'b1;
        wave_ready = wave_valid;
        @(posedge clk);
        #1;
        if (issue_valid !== 4'b0011)
            $fatal(1, "expected two issues, got %b", issue_valid);
        if (issue_wave0 !== 5'd21 || issue_wave1 !== 5'd3)
            $fatal(1, "unexpected circular sparse order %0d %0d", issue_wave0, issue_wave1);

        $display("global warp scheduler tests passed");
        $finish;
    end
endmodule
