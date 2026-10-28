// V298 MSHR admission macro, NOT an integrated GPU tile.
// POLICY: 0=work-conserving critical-first; 1=fixed one-credit reserve;
//         2=dependent-credit guard; 3=deadline-aware upper-bound controller.
// free_count is the number of currently available MSHRs AFTER returns are applied.
// dependent_known means the scoreboard has identified a future dependent miss;
// it does NOT guarantee that the dependent instruction will miss in a real GPU.
// bg_finishes_before_dep is an ORACLE signal and must never be treated as
// physically available without a separate latency predictor.
module v298_mshr_admission #(
    parameter integer POLICY = 2
) (
    input wire clk,
    input wire rst,
    input wire [2:0] free_count,
    input wire crit_ready,
    input wire bg_pending,
    input wire critical_return,
    input wire dependent_known,
    input wire dependent_cancel,
    input wire bg_finishes_before_dep,
    output wire crit_issue,
    output wire bg_issue,
    output reg guard_q
);
    wire has_credit = |free_count;
    wire last_credit = (free_count == 3'd1);
    wire block_bg;

    assign crit_issue = has_credit && crit_ready;
    assign block_bg =
        (POLICY == 0) ? 1'b0 :
        (POLICY == 1) ? last_credit :
        (POLICY == 2) ? (guard_q && last_credit) :
        (POLICY == 3) ? (guard_q && last_credit && !bg_finishes_before_dep) :
        1'b1;

    assign bg_issue = has_credit && !crit_ready && bg_pending && !block_bg;

    // State is updated only from visible return/dependency events, never
    // from future arrivals. The same state machine is present in all variants
    // for independent behavioral comparison; synthesis may optimize it away.
    always @(posedge clk) begin
        if (rst)
            guard_q <= 1'b0;
        else if (crit_issue || dependent_cancel)
            guard_q <= 1'b0;
        else if (critical_return && dependent_known)
            guard_q <= 1'b1;
    end
endmodule
