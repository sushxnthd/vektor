// Independent capacity-counting oracle for V310. This does NOT reuse the
// candidate's pairwise/triple conflict equations.
module tb_v310_verified_read_coalescer;
    reg [3:0] valid;
    reg [15:0] a;
    reg [15:0] b;
    reg [3:0] dup;
    wire [3:0] candidate;
    wire [3:0] baseline;
    reg [3:0] expected;
    reg [3:0] expected_base;
    integer combo, mask, digits, i, tested;

    vektor_v310_verified_read_coalescer dut (
        .request_valid(valid), .src0_bank_flat(a),
        .src1_bank_flat(b), .duplicate_verified(dup), .grant(candidate)
    );
    vektor_v310_compact_greedy_arbiter control (
        .request_valid(valid), .src0_bank_flat(a),
        .src1_bank_flat(b), .grant(baseline)
    );

    // Count every physical bank read for all simultaneously admitted requests.
    function integer safe_subset;
        input [3:0] subset;
        input [3:0] request_mask;
        input [15:0] src0, src1;
        input [3:0] same_register;
        integer bank, slot, demand;
        reg [3:0] ai, bi;
        begin
            safe_subset = ((subset & ~request_mask) == 4'b0000);
            for (bank = 0; bank < 16; bank = bank + 1) begin
                demand = 0;
                for (slot = 0; slot < 4; slot = slot + 1) begin
                    ai = src0[slot*4 +: 4];
                    bi = src1[slot*4 +: 4];
                    if (subset[slot]) begin
                        if (ai == bank) demand = demand + 1;
                        if (!(same_register[slot] && (ai == bi)) && (bi == bank))
                            demand = demand + 1;
                    end
                end
                if (demand > 2) safe_subset = 0;
            end
        end
    endfunction

    // Fixed-priority oracle greedily adds a slot only if every bank remains
    // within its independently counted two-port capacity.
    function [3:0] greedy_oracle;
        input [3:0] request_mask;
        input [15:0] src0, src1;
        input [3:0] same_register;
        integer slot;
        reg [3:0] chosen, trial;
        begin
            chosen = 4'b0;
            for (slot = 0; slot < 4; slot = slot + 1) begin
                trial = chosen;
                if (request_mask[slot]) begin
                    trial[slot] = 1'b1;
                    if (safe_subset(trial, request_mask, src0, src1, same_register))
                        chosen = trial;
                end
            end
            greedy_oracle = chosen;
        end
    endfunction

    task check;
        begin
            expected = greedy_oracle(valid,a,b,dup);
            expected_base = greedy_oracle(valid,a,b,4'b0000);
            if (candidate !== expected)
                $fatal(1, "V310_ORACLE_MISMATCH v=%h a=%h b=%h d=%h got=%h want=%h",
                       valid,a,b,dup,candidate,expected);
            if (baseline !== expected_base)
                $fatal(1, "V310_BASELINE_MISMATCH v=%h a=%h b=%h got=%h want=%h",
                       valid,a,b,baseline,expected_base);
            if (!safe_subset(candidate,valid,a,b,dup))
                $fatal(1, "V310_PORT_OVERSUBSCRIPTION");
            if ((dup == 4'b0000) && (candidate !== baseline))
                $fatal(1, "V310_ZERO_DUP_NO_WIN_VIOLATED");
            tested = tested + 1;
        end
    endtask

    initial begin
        tested = 0;
        // Frozen win: two valid requests, both operands bank zero, both
        // physically identical. Candidate reads once per request.
        valid = 4'b0011; a = 16'h0000; b = 16'h0000; dup = 4'b0011;
        #1; check();
        if (candidate !== 4'b0011 || baseline !== 4'b0001)
            $fatal(1, "V310_FROZEN_WIN_MOTIF_FAILED");

        // Frozen no-win: bank equality is NOT register equality.
        dup = 4'b0000;
        #1; check();
        if (candidate !== baseline)
            $fatal(1, "V310_BANK_EQUAL_NOT_REGISTER_EQUAL");

        // Malformed flag with unequal banks must be ignored defensively.
        valid = 4'b0011; a = 16'h0010; b = 16'h0021; dup = 4'b0011;
        #1; check();

        // No conflicts, all four admitted.
        valid = 4'b1111; a = 16'h6420; b = 16'h7531; dup = 4'b1111;
        #1; check();
        if (candidate !== 4'b1111 || baseline !== 4'b1111)
            $fatal(1, "V310_UNCONTESTED_NO_WIN_FAILED");

        // 3^8 * 16 = 104,976 reduced-bank cases with varying duplicate flags.
        for (combo = 0; combo < 6561; combo = combo + 1) begin
            digits = combo;
            for (i = 0; i < 4; i = i + 1) begin
                a[i*4 +: 4] = digits % 3;
                digits = digits / 3;
                b[i*4 +: 4] = digits % 3;
                digits = digits / 3;
            end
            for (mask = 0; mask < 16; mask = mask + 1) begin
                valid = mask[3:0];
                dup = (combo ^ mask) & 15;
                #1; check();
            end
        end
        if (tested != 104980)
            $fatal(1, "V310_FROZEN_TEST_COUNT %0d", tested);

        // Deterministic full-bank cases and mixed valid/duplicate masks.
        for (combo = 0; combo < 4096; combo = combo + 1) begin
            for (i = 0; i < 4; i = i + 1) begin
                a[i*4 +: 4] = (combo + 3*i + (combo >> 4)) & 15;
                b[i*4 +: 4] = ((combo * 7) + 5*i + (combo >> 6)) & 15;
            end
            valid = combo[3:0];
            dup = (combo >> 4) & 15;
            #1; check();
        end
        if (tested != 109076)
            $fatal(1, "V310_EXTENDED_TEST_COUNT %0d", tested);
        $display("V310_INDEPENDENT_RTL_ORACLE_PASS cases=%0d", tested);
        $finish;
    end
endmodule
