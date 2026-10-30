// Independent per-bank counting oracle for the V309 maximum-subset prefilter.
// Exhaustive over 16 validity masks and 3^8 reduced-bank assignments.
module tb_max_subset_arbiter;
    reg [3:0] valid;
    reg [15:0] bank0;
    reg [15:0] bank1;
    wire [3:0] optimal;
    wire [3:0] greedy;
    integer combo;
    integer mask;
    integer digits;
    integer i;
    integer tested;
    reg [3:0] expected;

    vektor_v309_max_subset_arbiter dut (
        .request_valid(valid), .src0_bank_flat(bank0),
        .src1_bank_flat(bank1), .grant(optimal)
    );
    vektor_rf_bank_arbiter incumbent (
        .request_valid(valid), .src0_bank_flat(bank0),
        .src1_bank_flat(bank1), .grant(greedy)
    );

    function integer count_bits(input [3:0] x);
        integer j;
        begin
            count_bits = 0;
            for (j = 0; j < 4; j = j + 1)
                if (x[j]) count_bits = count_bits + 1;
        end
    endfunction

    function integer safe_subset(
        input [3:0] subset,
        input [3:0] request_mask,
        input [15:0] a,
        input [15:0] b
    );
        integer k;
        integer bank;
        integer demand;
        begin
            safe_subset = ((subset & ~request_mask) == 4'b0000);
            for (bank = 0; bank < 16; bank = bank + 1) begin
                demand = 0;
                for (k = 0; k < 4; k = k + 1) begin
                    if (subset[k]) begin
                        if (a[k*4 +: 4] == bank) demand = demand + 1;
                        if (b[k*4 +: 4] == bank) demand = demand + 1;
                    end
                end
                if (demand > 2) safe_subset = 0;
            end
        end
    endfunction

    function [3:0] reference_optimum(
        input [3:0] request_mask,
        input [15:0] a,
        input [15:0] b
    );
        integer s;
        integer best_score;
        reg [3:0] best_mask;
        begin
            best_mask = 4'b0000;
            best_score = 0;
            for (s = 0; s < 16; s = s + 1) begin
                if (safe_subset(s[3:0], request_mask, a, b) &&
                    count_bits(s[3:0]) > best_score) begin
                    best_score = count_bits(s[3:0]);
                    best_mask = s[3:0];
                end
            end
            reference_optimum = best_mask;
        end
    endfunction

    task check;
        begin
            expected = reference_optimum(valid, bank0, bank1);
            if (optimal !== expected) begin
                $display("FAIL_OPT valid=%h a=%h b=%h got=%h expected=%h",
                         valid, bank0, bank1, optimal, expected);
                $fatal(1);
            end
            if (!safe_subset(optimal, valid, bank0, bank1) ||
                !safe_subset(greedy, valid, bank0, bank1)) begin
                $display("FAIL_PORTS valid=%h a=%h b=%h opt=%h greedy=%h",
                         valid, bank0, bank1, optimal, greedy);
                $fatal(1);
            end
            if (count_bits(optimal) < count_bits(greedy)) begin
                $display("FAIL_REGRET opt=%h greedy=%h", optimal, greedy);
                $fatal(1);
            end
            tested = tested + 1;
        end
    endtask

    initial begin
        tested = 0;
        valid = 4'hf;
        bank0 = {4'd2,4'd1,4'd0,4'd0};
        bank1 = {4'd2,4'd1,4'd0,4'd1};
        #1;
        check();
        if (greedy !== 4'h9 || optimal !== 4'he)
            $fatal(1, "FAIL_WIN_MOTIF greedy=%h optimal=%h", greedy, optimal);

        valid = 4'hf;
        bank0 = {4'd6,4'd4,4'd2,4'd0};
        bank1 = {4'd7,4'd5,4'd3,4'd1};
        #1;
        check();
        if (greedy !== 4'hf || optimal !== 4'hf)
            $fatal(1, "FAIL_NO_WIN_MOTIF");

        valid = 4'hf;
        bank0 = 16'hffff;
        bank1 = 16'hffff;
        #1;
        check();
        if (optimal !== 4'h1)
            $fatal(1, "FAIL_SAME_BANK_TWO_READS");

        // Distinct high bank IDs, invalid-request cases and same-bank loads.
        valid = 4'h5;
        bank0 = 16'hfedc;
        bank1 = 16'hfedc;
        #1;
        check();

        // 3^8 * 16 = 104,976 input vectors.
        for (combo = 0; combo < 6561; combo = combo + 1) begin
            digits = combo;
            for (i = 0; i < 4; i = i + 1) begin
                bank0[i*4 +: 4] = digits % 3;
                digits = digits / 3;
                bank1[i*4 +: 4] = digits % 3;
                digits = digits / 3;
            end
            for (mask = 0; mask < 16; mask = mask + 1) begin
                valid = mask[3:0];
                #1;
                check();
            end
        end
        if (tested != 104980) $fatal(1, "FAIL_TEST_COUNT %0d", tested);
        $display("V309_MAX_SUBSET_ORACLE_PASS cases=%0d", tested);
        $finish;
    end
endmodule
