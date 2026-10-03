`timescale 1ns/1ps

module tb_issue_control;
    logic clk = 1'b0;
    logic rst_n = 1'b0;
    logic [31:0] wave_valid;
    logic [31:0] wave_ready;
    logic [127:0] src0_bank_by_wave;
    logic [127:0] src1_bank_by_wave;
    logic [3:0] issue_valid;
    logic [4:0] issue_wave0;
    logic [4:0] issue_wave1;
    logic [4:0] issue_wave2;
    logic [4:0] issue_wave3;

    vektor_issue_control dut (
        .clk(clk), .rst_n(rst_n),
        .wave_valid(wave_valid), .wave_ready(wave_ready),
        .src0_bank_by_wave(src0_bank_by_wave),
        .src1_bank_by_wave(src1_bank_by_wave),
        .issue_valid(issue_valid),
        .issue_wave0(issue_wave0), .issue_wave1(issue_wave1),
        .issue_wave2(issue_wave2), .issue_wave3(issue_wave3)
    );

    always #5 clk = ~clk;

    task set_banks(input integer wave, input [3:0] b0, input [3:0] b1);
        begin
            src0_bank_by_wave[wave*4 +: 4] = b0;
            src1_bank_by_wave[wave*4 +: 4] = b1;
        end
    endtask

    task reset_dut;
        begin
            wave_valid = '0;
            wave_ready = '0;
            src0_bank_by_wave = '0;
            src1_bank_by_wave = '0;
            rst_n = 1'b0;
            repeat (2) @(posedge clk);
            rst_n = 1'b1;
            #1;
        end
    endtask

    initial begin
        reset_dut();

        // Four partitions with nonconflicting operand banks all issue.
        wave_valid[0] = 1'b1;
        wave_valid[8] = 1'b1;
        wave_valid[16] = 1'b1;
        wave_valid[24] = 1'b1;
        wave_ready = wave_valid;
        set_banks(0,  4'd0, 4'd1);
        set_banks(8,  4'd2, 4'd3);
        set_banks(16, 4'd4, 4'd5);
        set_banks(24, 4'd6, 4'd7);
        #1;
        if (issue_valid !== 4'b1111)
            $fatal(1, "nonconflicting waves should all issue, got %b", issue_valid);

        // Four waves all demand the same same-bank pair. The dual-read bank
        // capacity admits only one request; the others must remain pending.
        reset_dut();
        wave_valid[0] = 1'b1;
        wave_valid[8] = 1'b1;
        wave_valid[16] = 1'b1;
        wave_valid[24] = 1'b1;
        wave_ready = wave_valid;
        set_banks(0,  4'd0, 4'd0);
        set_banks(8,  4'd0, 4'd0);
        set_banks(16, 4'd0, 4'd0);
        set_banks(24, 4'd0, 4'd0);
        #1;
        if (issue_valid !== 4'b0001)
            $fatal(1, "expected one admitted conflict request, got %b", issue_valid);
        if (issue_wave0 !== 5'd0)
            $fatal(1, "expected wave 0 to win first conflict, got %0d", issue_wave0);

        // Model external retirement of the accepted wave only. All rejected
        // waves remain ready and must be presented again next cycle.
        @(posedge clk);
        wave_valid[0] = 1'b0;
        wave_ready[0] = 1'b0;
        #1;
        if (issue_valid === 4'b0000)
            $fatal(1, "blocked waves were lost instead of retried");
        if (issue_wave0 !== 5'd8 && issue_wave1 !== 5'd8 &&
            issue_wave2 !== 5'd8 && issue_wave3 !== 5'd8)
            $fatal(1, "wave 8 was not retried after wave 0 retired");

        // Partial conflict: bank 0 can serve two reads total. Slots 0 and 1
        // collide on both operands; independent slots remain admissible.
        reset_dut();
        wave_valid[0] = 1'b1;
        wave_valid[8] = 1'b1;
        wave_valid[16] = 1'b1;
        wave_valid[24] = 1'b1;
        wave_ready = wave_valid;
        set_banks(0,  4'd0, 4'd1);
        set_banks(8,  4'd0, 4'd1);
        set_banks(16, 4'd4, 4'd5);
        set_banks(24, 4'd6, 4'd7);
        #1;
        if (issue_valid !== 4'b1101)
            $fatal(1, "expected slot1 rejection with slots0/2/3 accepted, got %b", issue_valid);

        $display("issue control tests passed");
        $finish;
    end
endmodule
