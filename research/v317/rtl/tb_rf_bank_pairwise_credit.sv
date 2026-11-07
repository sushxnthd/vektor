// Independent operand-count oracle for source and pairwise RTL.
// 4 phases x (4096 exhaustive two-bank + 16 directed full-bank +
// 1024 seeded full-bank random) + reset/wrap = 20,545 checks.
module tb_v317_rf_pairwise_credit;
    reg clk = 0;
    reg reset = 0;
    reg [3:0] request_valid = 0;
    reg [15:0] src0_bank_flat = 0;
    reg [15:0] src1_bank_flat = 0;
    wire [3:0] fixed_source, fixed_pairwise;
    wire [3:0] rotating_source, rotating_pairwise;
    integer phase_idx, phase_expected, mask_idx, encoding;
    integer slot, bank, trial, seed, checks = 0;
    integer reads [0:15];

    vektor_rf_bank_arbiter ref_fixed (
        .request_valid(request_valid), .src0_bank_flat(src0_bank_flat),
        .src1_bank_flat(src1_bank_flat), .grant(fixed_source)
    );
    vektor_v317_rf_pairwise candidate_fixed (
        .request_valid(request_valid), .src0_bank_flat(src0_bank_flat),
        .src1_bank_flat(src1_bank_flat), .grant(fixed_pairwise)
    );
    vektor_v317_rf_rotating ref_rotating (
        .clk(clk), .reset(reset),
        .request_valid(request_valid), .src0_bank_flat(src0_bank_flat),
        .src1_bank_flat(src1_bank_flat), .grant(rotating_source)
    );
    vektor_v317_rf_pairwise_rotating candidate_rotating (
        .clk(clk), .reset(reset),
        .request_valid(request_valid), .src0_bank_flat(src0_bank_flat),
        .src1_bank_flat(src1_bank_flat), .grant(rotating_pairwise)
    );

    task automatic oracle(input integer phase, output reg [3:0] answer);
        integer k, s, a, b, t;
        reg permitted;
        begin
            for (t = 0; t < 16; t = t + 1)
                reads[t] = 0;
            answer = 0;
            for (k = 0; k < 4; k = k + 1) begin
                s = (phase + k) % 4;
                a = (src0_bank_flat >> (4*s)) & 15;
                b = (src1_bank_flat >> (4*s)) & 15;
                permitted = 0;
                if (request_valid[s]) begin
                    if (a == b)
                        permitted = (reads[a] == 0);
                    else
                        permitted = (reads[a] < 2 && reads[b] < 2);
                    if (permitted) begin
                        answer[s] = 1'b1;
                        reads[a] = reads[a] + 1;
                        reads[b] = reads[b] + 1;
                    end
                end
            end
            for (t = 0; t < 16; t = t + 1)
                if (reads[t] > 2)
                    $fatal(1, "oracle overgranted bank=%0d", t);
        end
    endtask

    task automatic verify;
        reg [3:0] expected_fixed, expected_rotating;
        begin
            oracle(0, expected_fixed);
            oracle(phase_expected, expected_rotating);
            #1;
            if (fixed_source !== expected_fixed ||
                fixed_pairwise !== expected_fixed ||
                rotating_source !== expected_rotating ||
                rotating_pairwise !== expected_rotating)
                $fatal(1,
                    "phase=%0d valid=%b a=%h b=%h fixed=%b/%b expected=%b rot=%b/%b expected=%b",
                    phase_expected, request_valid, src0_bank_flat,
                    src1_bank_flat, fixed_source, fixed_pairwise, expected_fixed,
                    rotating_source, rotating_pairwise, expected_rotating);
            checks = checks + 1;
        end
    endtask

    initial begin
        seed = 317011;
        reset = 1;
        #2;
        reset = 0;
        #1;
        // Prime the source always @* block: an all-zero first vector
        // can otherwise leave an untriggered combinational output at X.
        request_valid = 4'b1111;
        src0_bank_flat = 16'hffff;
        src1_bank_flat = 16'h0123;
        #1;
        for (phase_idx = 0; phase_idx < 4; phase_idx = phase_idx + 1) begin
            phase_expected = phase_idx;
            for (mask_idx = 0; mask_idx < 16; mask_idx = mask_idx + 1) begin
                request_valid = mask_idx[3:0];
                for (encoding = 0; encoding < 256; encoding = encoding + 1) begin
                    src0_bank_flat = 0;
                    src1_bank_flat = 0;
                    for (slot = 0; slot < 4; slot = slot + 1) begin
                        src0_bank_flat[slot*4 +: 4] =
                            (encoding >> (2*slot)) & 1;
                        src1_bank_flat[slot*4 +: 4] =
                            (encoding >> (2*slot+1)) & 1;
                    end
                    verify();
                end
            end
            request_valid = 4'b1111;
            for (bank = 0; bank < 16; bank = bank + 1) begin
                for (slot = 0; slot < 4; slot = slot + 1) begin
                    src0_bank_flat[slot*4 +: 4] = bank;
                    src1_bank_flat[slot*4 +: 4] = (bank + slot) % 16;
                end
                verify();
            end
            for (trial = 0; trial < 1024; trial = trial + 1) begin
                request_valid = $random(seed);
                src0_bank_flat = $random(seed);
                src1_bank_flat = $random(seed);
                verify();
            end
            clk = 1;
            #1;
            clk = 0;
            #1;
        end
        phase_expected = 0;
        request_valid = 4'b1111;
        verify();
        if (checks != 20545)
            $fatal(1, "incorrect case count %0d", checks);
        $display("PASS V317 pairwise bank credit: %0d independent oracle cases", checks);
        $finish;
    end
endmodule
