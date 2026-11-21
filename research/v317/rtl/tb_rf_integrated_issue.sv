`timescale 1ns/1ps
// Source-faithful integrated scheduler + RF grant equivalence regression.
// Deterministic random stream, directed same-bank/hotspot and all-ready cases.
module tb_rf_integrated_issue;
    reg clk = 1'b0;
    always #5 clk = ~clk;
    reg rst_n = 1'b0;
    reg [31:0] wave_valid = 0, wave_ready = 0;
    reg [127:0] src0_bank_by_wave = 0, src1_bank_by_wave = 0;
    wire [3:0] source_valid, pair_valid;
    wire [19:0] source_waves, pair_waves;
    integer seed = 32'h31702026;
    integer cycle, j, mode;
    integer accepted = 0;

    vektor_v317_issue_integrated_top_source source (
        .clk(clk), .rst_n(rst_n), .wave_valid(wave_valid), .wave_ready(wave_ready),
        .src0_bank_by_wave(src0_bank_by_wave), .src1_bank_by_wave(src1_bank_by_wave),
        .issue_valid_q(source_valid), .issue_wave_flat_q(source_waves)
    );
    vektor_v317_issue_integrated_top_pairwise pairwise (
        .clk(clk), .rst_n(rst_n), .wave_valid(wave_valid), .wave_ready(wave_ready),
        .src0_bank_by_wave(src0_bank_by_wave), .src1_bank_by_wave(src1_bank_by_wave),
        .issue_valid_q(pair_valid), .issue_wave_flat_q(pair_waves)
    );

    initial begin
        repeat (3) @(negedge clk);
        rst_n = 1'b1;
        for (cycle = 0; cycle < 4096; cycle = cycle + 1) begin
            @(negedge clk);
            mode = cycle % 8;
            wave_valid = (mode == 0) ? 32'hffffffff : $random(seed);
            wave_ready = (mode == 1) ? 32'hffffffff : $random(seed);
            src0_bank_by_wave = 0;
            src1_bank_by_wave = 0;
            for (j = 0; j < 32; j = j + 1) begin
                if (mode == 2) begin
                    src0_bank_by_wave[4*j +: 4] = 4'd0;
                    src1_bank_by_wave[4*j +: 4] = 4'd0;
                end else if (mode == 3) begin
                    src0_bank_by_wave[4*j +: 4] = j % 16;
                    src1_bank_by_wave[4*j +: 4] = (j + 1) % 16;
                end else if (mode == 4) begin
                    src0_bank_by_wave[4*j +: 4] = j % 2;
                    src1_bank_by_wave[4*j +: 4] = (j + 1) % 2;
                end else begin
                    src0_bank_by_wave[4*j +: 4] = $random(seed);
                    src1_bank_by_wave[4*j +: 4] = $random(seed);
                end
            end
            @(posedge clk);
            #1;
            if (source_valid !== pair_valid || source_waves !== pair_waves) begin
                $display("FAIL cycle=%0d source=%b/%h pair=%b/%h",
                    cycle, source_valid, source_waves, pair_valid, pair_waves);
                $fatal(1, "Integrated issue-control equivalence mismatch");
            end
            accepted = accepted + source_valid[0] + source_valid[1]
                       + source_valid[2] + source_valid[3];
        end
        $display("PASS V317 integrated issue-control equivalence cycles=%0d accepted=%0d",
            cycle, accepted);
        $finish;
    end
endmodule
