`timescale 1ns/1ps
// V317 prospective three-way RF proxy: 4096-cycle source/pairwise/compact equivalence.
module tb_rf_proxy_compact_challenger;
    reg clk = 0;
    always #5 clk = ~clk;
    reg rst_n = 0;
    reg [31:0] wave_valid = 0, wave_ready = 0;
    reg [127:0] src0_bank_by_wave = 0, src1_bank_by_wave = 0;
    reg wr_en = 0;
    reg [3:0] wr_bank = 0;
    reg [1:0] wr_row = 0;
    reg [7:0] wr_data = 0;
    wire [3:0] src_valid, pair_valid;
    wire [19:0] src_wave, pair_wave;
    wire [63:0] src_data, pair_data;
    wire src_overflow, pair_overflow;
    wire [3:0] compact_valid;
    wire [19:0] compact_wave;
    wire [63:0] compact_data;
    wire compact_overflow;
    integer seed = 32'h31702026;
    integer cycle, j, mode, accepted = 0, tested = 0;

    vektor_v317_rf_proxy_top_source source (
        .clk(clk), .rst_n(rst_n), .wave_valid(wave_valid), .wave_ready(wave_ready),
        .src0_bank_by_wave(src0_bank_by_wave), .src1_bank_by_wave(src1_bank_by_wave),
        .wr_en(wr_en), .wr_bank(wr_bank), .wr_row(wr_row), .wr_data(wr_data),
        .issue_valid_sink_q(src_valid), .issue_wave_sink_q(src_wave),
        .operands_q(src_data), .overflow_q(src_overflow)
    );
    vektor_v317_rf_proxy_top_pairwise pairwise (
        .clk(clk), .rst_n(rst_n), .wave_valid(wave_valid), .wave_ready(wave_ready),
        .src0_bank_by_wave(src0_bank_by_wave), .src1_bank_by_wave(src1_bank_by_wave),
        .wr_en(wr_en), .wr_bank(wr_bank), .wr_row(wr_row), .wr_data(wr_data),
        .issue_valid_sink_q(pair_valid), .issue_wave_sink_q(pair_wave),
        .operands_q(pair_data), .overflow_q(pair_overflow)
    );
    vektor_v317_rf_proxy_top_compact compact (
        .clk(clk), .rst_n(rst_n), .wave_valid(wave_valid), .wave_ready(wave_ready),
        .src0_bank_by_wave(src0_bank_by_wave), .src1_bank_by_wave(src1_bank_by_wave),
        .wr_en(wr_en), .wr_bank(wr_bank), .wr_row(wr_row), .wr_data(wr_data),
        .issue_valid_sink_q(compact_valid), .issue_wave_sink_q(compact_wave),
        .operands_q(compact_data), .overflow_q(compact_overflow)
    );
    initial begin
        repeat (3) @(negedge clk);
        rst_n = 1;
        // Initialize all 64 physical RF-proxy words before measuring reads.
        for (j = 0; j < 64; j = j + 1) begin
            @(negedge clk);
            wr_en = 1;
            wr_bank = j / 4;
            wr_row = j % 4;
            wr_data = (j * 13) ^ 8'h5a;
        end
        @(negedge clk);
        wr_en = 0;
        repeat (4) @(negedge clk);
        for (cycle = 0; cycle < 4096; cycle = cycle + 1) begin
            @(negedge clk);
            mode = cycle % 8;
            wave_valid = (mode == 0 || mode == 2 || mode == 3) ? 32'hffffffff : $random(seed);
            wave_ready = (mode == 1 || mode == 2 || mode == 3) ? 32'hffffffff : $random(seed);
            src0_bank_by_wave = 0;
            src1_bank_by_wave = 0;
            for (j = 0; j < 32; j = j + 1) begin
                if (mode == 2) begin
                    src0_bank_by_wave[4*j +: 4] = 4'd0;
                    src1_bank_by_wave[4*j +: 4] = 4'd0;
                end else if (mode == 3) begin
                    src0_bank_by_wave[4*j +: 4] = j % 2;
                    src1_bank_by_wave[4*j +: 4] = (j + 1) % 2;
                end else if (mode == 4) begin
                    src0_bank_by_wave[4*j +: 4] = j % 16;
                    src1_bank_by_wave[4*j +: 4] = (j + 1) % 16;
                end else begin
                    src0_bank_by_wave[4*j +: 4] = $random(seed);
                    src1_bank_by_wave[4*j +: 4] = $random(seed);
                end
            end
            wr_en = (cycle % 11 == 0);
            wr_bank = $random(seed);
            wr_row = $random(seed);
            wr_data = $random(seed);
            @(posedge clk);
            #1;
            if (src_valid !== pair_valid || src_wave !== pair_wave ||
                src_data !== pair_data || src_overflow !== pair_overflow ||
                src_valid !== compact_valid || src_wave !== compact_wave ||
                src_data !== compact_data || src_overflow !== compact_overflow) begin
                $display("FAIL cycle=%0d src_valid=%b pair_valid=%b src_wave=%h pair_wave=%h src_data=%h pair_data=%h src_overflow=%b pair_overflow=%b",
                    cycle, src_valid, pair_valid, src_wave, pair_wave, src_data, pair_data, src_overflow, pair_overflow);
                $fatal(1, "RF-proxy integrated equivalence mismatch");
            end
            if (src_overflow !== 1'b0 || pair_overflow !== 1'b0 || compact_overflow !== 1'b0)
                $fatal(1, "RF proxy bank read ports oversubscribed");
            accepted = accepted + src_valid[0] + src_valid[1] + src_valid[2] + src_valid[3];
            tested = tested + 1;
        end
        $display("PASS V317 compact challenger cycles=%0d accepted=%0d overflow=0", tested, accepted);
        $finish;
    end
endmodule
