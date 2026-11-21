// Independent reference for V317 rotating-priority RTL. Do NOT reuse
// the source arbiter's used_once/used_twice algorithm in the oracle.
module tb_v317_rf_bank_rotating;
    reg clk = 0;
    reg reset = 0;
    reg [3:0] request_valid = 0;
    reg [15:0] src0_bank_flat = 0;
    reg [15:0] src1_bank_flat = 0;
    wire [3:0] grant;
    integer phase_idx;
    integer mask_idx;
    integer encoding;
    integer slot;
    integer a;
    integer b;
    integer checks = 0;
    integer phase_expected = 0;
    integer reads [0:15];
    reg [3:0] expected;
    reg admissible;
    integer offset;
    integer bank;

    vektor_v317_rf_rotating dut (
        .clk(clk), .reset(reset),
        .request_valid(request_valid),
        .src0_bank_flat(src0_bank_flat),
        .src1_bank_flat(src1_bank_flat),
        .grant(grant)
    );

    task automatic verify;
        integer k;
        integer s;
        integer a_local;
        integer b_local;
        reg [3:0] oracle;
        reg can_grant;
        begin
            for (k = 0; k < 16; k = k + 1)
                reads[k] = 0;
            oracle = 0;
            for (k = 0; k < 4; k = k + 1) begin
                s = (phase_expected + k) % 4;
                a_local = (src0_bank_flat >> (4*s)) & 15;
                b_local = (src1_bank_flat >> (4*s)) & 15;
                can_grant = 0;
                if (request_valid[s]) begin
                    if (a_local == b_local)
                        can_grant = (reads[a_local] == 0);
                    else
                        can_grant = (reads[a_local] < 2 && reads[b_local] < 2);
                    if (can_grant) begin
                        oracle[s] = 1'b1;
                        reads[a_local] = reads[a_local] + 1;
                        reads[b_local] = reads[b_local] + 1;
                    end
                end
            end
            #1;
            if (grant !== oracle)
                $fatal(1, "mismatch phase=%0d valid=%b a=%h b=%h got=%b expected=%b",
                    phase_expected, request_valid, src0_bank_flat, src1_bank_flat,
                    grant, oracle);
            for (k = 0; k < 16; k = k + 1)
                if (reads[k] > 2)
                    $fatal(1, "oracle exceeded physical bank port capacity");
            checks = checks + 1;
        end
    endtask

    initial begin
        reset = 1;
        #2;
        reset = 0;
        #1;
        for (phase_idx = 0; phase_idx < 4; phase_idx = phase_idx + 1) begin
            phase_expected = phase_idx;
            for (mask_idx = 0; mask_idx < 16; mask_idx = mask_idx + 1) begin
                request_valid = mask_idx[3:0];
                for (encoding = 0; encoding < 256; encoding = encoding + 1) begin
                    src0_bank_flat = 0;
                    src1_bank_flat = 0;
                    for (slot = 0; slot < 4; slot = slot + 1) begin
                        src0_bank_flat[slot*4 +: 4] = (encoding >> (2*slot)) & 1;
                        src1_bank_flat[slot*4 +: 4] = (encoding >> (2*slot+1)) & 1;
                    end
                    verify();
                end
            end
            // Directed all-16-bank tests include equal-register-bank reads,
            // hot-bank collisions and independent pairs at each phase.
            request_valid = 4'b1111;
            for (bank = 0; bank < 16; bank = bank + 1) begin
                for (slot = 0; slot < 4; slot = slot + 1) begin
                    src0_bank_flat[slot*4 +: 4] = bank;
                    src1_bank_flat[slot*4 +: 4] = (bank + slot) % 16;
                end
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
        if (checks != (4*4096 + 4*16 + 1))
            $fatal(1, "incorrect test count: %0d", checks);
        $display("PASS rotating-priority independent oracle: %0d cases", checks);
        $finish;
    end
endmodule
