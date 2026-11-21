// Independent exhaustive oracle for V317 exact RF issue challenger.
// Both DUTs have the SAME 4 slots, 16 banks and 2 reads/bank.
// The exhaustive oracle independently counts both operands, including same-bank.
module tb_v317_rf_bank_exact;
    reg [3:0] request_valid;
    reg [15:0] src0_bank_flat, src1_bank_flat;
    wire [3:0] exact_grant, priority_grant;
    integer valid_id, pattern, slot_id;
    integer cand, bank_id, req, demand, count, best_count;
    integer total_priority, total_exact, suboptimal, cases;
    reg [3:0] best, mask;
    reg allowed;

    vektor_v317_rf_bank_exact exact_dut (
        .request_valid(request_valid), .src0_bank_flat(src0_bank_flat),
        .src1_bank_flat(src1_bank_flat), .grant(exact_grant)
    );
    vektor_rf_bank_arbiter priority_dut (
        .request_valid(request_valid), .src0_bank_flat(src0_bank_flat),
        .src1_bank_flat(src1_bank_flat), .grant(priority_grant)
    );

    function integer popcount;
        input [3:0] value;
        integer bit_id;
        begin
            popcount = 0;
            for (bit_id=0; bit_id<4; bit_id=bit_id+1)
                if (value[bit_id]) popcount = popcount + 1;
        end
    endfunction

    task check_case;
        begin
            #1;
            best = 0;
            best_count = -1;
            for (cand=0; cand<16; cand=cand+1) begin
                mask = cand[3:0];
                allowed = ((mask & ~request_valid) == 0);
                for (bank_id=0; bank_id<16; bank_id=bank_id+1) begin
                    demand = 0;
                    for (req=0; req<4; req=req+1) begin
                        if (mask[req]) begin
                            if (src0_bank_flat[req*4 +: 4] == bank_id)
                                demand = demand + 1;
                            if (src1_bank_flat[req*4 +: 4] == bank_id)
                                demand = demand + 1;
                        end
                    end
                    if (demand > 2) allowed = 0;
                end
                count = popcount(mask);
                if (allowed && ((count > best_count) ||
                    ((count == best_count) && (mask > best)))) begin
                    best_count = count;
                    best = mask;
                end
            end
            if (exact_grant !== best)
                $fatal(1, "exact mismatch valid=%h src0=%h src1=%h got=%h want=%h",
                    request_valid, src0_bank_flat, src1_bank_flat, exact_grant, best);
            if ((priority_grant & ~request_valid) != 0)
                $fatal(1, "priority granted invalid request");
            for (bank_id=0; bank_id<16; bank_id=bank_id+1) begin
                demand = 0;
                for (req=0; req<4; req=req+1)
                    if (priority_grant[req]) begin
                        if (src0_bank_flat[req*4 +: 4] == bank_id)
                            demand = demand + 1;
                        if (src1_bank_flat[req*4 +: 4] == bank_id)
                            demand = demand + 1;
                    end
                if (demand > 2) $fatal(1, "priority overgrant");
            end
            if (popcount(priority_grant) > popcount(exact_grant))
                $fatal(1, "priority exceeds exact maximum");
            cases = cases + 1;
            total_priority = total_priority + popcount(priority_grant);
            total_exact = total_exact + popcount(exact_grant);
            if (popcount(priority_grant) < popcount(exact_grant))
                suboptimal = suboptimal + 1;
        end
    endtask

    initial begin
        request_valid=0; src0_bank_flat=0; src1_bank_flat=0;
        cases=0; total_priority=0; total_exact=0; suboptimal=0;

        // Frozen win: (0,0),(0,1),(0,1), slot 3 invalid.
        request_valid=4'b0111;
        src0_bank_flat=16'h0000; src1_bank_flat=16'h0110;
        #1;
        if (priority_grant !== 4'b0001 || exact_grant !== 4'b0110)
            $fatal(1, "frozen predicted-win witness failed");
        check_case();

        // Frozen no-win: (0,0),(1,1).
        request_valid=4'b0011;
        src0_bank_flat=16'h0010; src1_bank_flat=16'h0010;
        #1;
        if (priority_grant !== 4'b0011 || exact_grant !== 4'b0011)
            $fatal(1, "frozen predicted-no-win witness failed");
        check_case();

        // Every two-bank pair encoding for each of four slots, all valid masks.
        for (valid_id=0; valid_id<16; valid_id=valid_id+1) begin
            for (pattern=0; pattern<256; pattern=pattern+1) begin
                request_valid=valid_id[3:0];
                src0_bank_flat=0; src1_bank_flat=0;
                for (slot_id=0; slot_id<4; slot_id=slot_id+1) begin
                    src0_bank_flat[4*slot_id +: 4] = (pattern >> (2*slot_id)) & 1;
                    src1_bank_flat[4*slot_id +: 4] = (pattern >> (2*slot_id+1)) & 1;
                end
                check_case();
            end
        end
        // Include two extra frozen witness calls in totals.
        if (cases != 4098 || suboptimal != 245 ||
            total_priority != 5213 || total_exact != 5458)
            $fatal(1, "exhaustive count mismatch cases=%0d subopt=%0d priority=%0d exact=%0d",
                cases, suboptimal, total_priority, total_exact);
        $display("PASS: 4096 exhaustive two-bank configurations + two frozen witnesses");
        $display("priority_grants=%0d exact_grants=%0d suboptimal_cases=%0d",
            total_priority, total_exact, suboptimal);
        $finish;
    end
endmodule
