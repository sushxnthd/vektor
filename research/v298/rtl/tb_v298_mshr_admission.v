// Independent exhaustive clocked truth-table test for the V298 admission macro.
// This verifies the controller interface only, not a complete MSHR allocator.
module tb_v298_mshr_admission;
    reg clk, rst;
    reg [2:0] free_count;
    reg crit_ready, bg_pending, critical_return, dependent_known;
    reg dependent_cancel, bg_finishes_before_dep;
    wire [3:0] crit_issue, bg_issue, guard_q;
    genvar p;
    generate
        for (p = 0; p < 4; p = p + 1) begin : dut
            v298_mshr_admission #(.POLICY(p)) core (
                .clk(clk), .rst(rst), .free_count(free_count),
                .crit_ready(crit_ready), .bg_pending(bg_pending),
                .critical_return(critical_return),
                .dependent_known(dependent_known),
                .dependent_cancel(dependent_cancel),
                .bg_finishes_before_dep(bg_finishes_before_dep),
                .crit_issue(crit_issue[p]), .bg_issue(bg_issue[p]),
                .guard_q(guard_q[p])
            );
        end
    endgenerate

    integer initial_guard, free_slots, flags, policy, checked;
    reg exp_crit, exp_bg, exp_block, exp_next;

    initial begin
        clk = 0; rst = 0; free_count = 0;
        crit_ready = 0; bg_pending = 0; critical_return = 0;
        dependent_known = 0; dependent_cancel = 0;
        bg_finishes_before_dep = 0; checked = 0;

        for (initial_guard = 0; initial_guard < 2; initial_guard = initial_guard + 1)
        for (free_slots = 0; free_slots <= 4; free_slots = free_slots + 1)
        for (flags = 0; flags < 64; flags = flags + 1) begin
            // Reset, then optionally create a genuine registered guard event.
            clk = 0; rst = 1;
            free_count = 0; crit_ready = 0; bg_pending = 0;
            critical_return = 0; dependent_known = 0;
            dependent_cancel = 0; bg_finishes_before_dep = 0;
            #1 clk = 1; #1 clk = 0; rst = 0;
            if (initial_guard == 1) begin
                critical_return = 1; dependent_known = 1;
                #1 clk = 1; #1 clk = 0;
            end
            free_count = free_slots;
            crit_ready = flags[0];
            bg_pending = flags[1];
            critical_return = flags[2];
            dependent_known = flags[3];
            dependent_cancel = flags[4];
            bg_finishes_before_dep = flags[5];
            #1;
            exp_crit = (free_slots > 0) && crit_ready;
            exp_next = exp_crit || dependent_cancel ? 1'b0 :
                       critical_return && dependent_known ? 1'b1 :
                       (initial_guard == 1);
            for (policy = 0; policy < 4; policy = policy + 1) begin
                exp_block = (policy == 1 && free_slots == 1) ||
                            (policy == 2 && initial_guard == 1 && free_slots == 1) ||
                            (policy == 3 && initial_guard == 1 && free_slots == 1 &&
                             !bg_finishes_before_dep);
                exp_bg = (free_slots > 0) && !crit_ready && bg_pending && !exp_block;
                if (crit_issue[policy] !== exp_crit ||
                    bg_issue[policy] !== exp_bg ||
                    guard_q[policy] !== (initial_guard == 1)) begin
                    $display("FAIL pre policy=%0d guard=%0d free=%0d flags=%0d ci=%b bi=%b gq=%b expected=%b,%b",
                             policy, initial_guard, free_slots, flags,
                             crit_issue[policy], bg_issue[policy], guard_q[policy],
                             exp_crit, exp_bg);
                    $fatal(1);
                end
                checked = checked + 1;
            end
            #1 clk = 1; #1;
            for (policy = 0; policy < 4; policy = policy + 1) begin
                if (guard_q[policy] !== exp_next) begin
                    $display("FAIL next policy=%0d guard=%0d free=%0d flags=%0d expected=%b got=%b",
                             policy, initial_guard, free_slots, flags,
                             exp_next, guard_q[policy]);
                    $fatal(1);
                end
            end
            clk = 0;
        end
        if (checked != 2560) $fatal(1, "Unexpected coverage %0d", checked);
        $display("PASS V298 2560 controller output vectors + 2560 next-state checks");
        $finish;
    end
endmodule
