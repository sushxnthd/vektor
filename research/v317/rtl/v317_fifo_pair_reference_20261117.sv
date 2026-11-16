// Strict-order two-request, two-bank-port reference scheduler.
// Research control only; NOT a GPU warp scheduler or validated V296 datapath.
// Both requests are assumed to have one bank access. Each bank has one service
// port per cycle. No request may overtake an older valid request.
module v317_fifo_pair_reference #(
    parameter integer BANK_BITS = 4
) (
    input  wire                   head_valid,
    input  wire [BANK_BITS-1:0]   head_bank,
    input  wire                   next_valid,
    input  wire [BANK_BITS-1:0]   next_bank,
    input  wire                   downstream_ready,
    output wire                   issue_head,
    output wire                   issue_next
);
    wire bank_distinct = (head_bank != next_bank);
    assign issue_head = downstream_ready && head_valid;
    assign issue_next = issue_head && next_valid && bank_distinct;
endmodule

// The ordering contract is deliberately stronger than bank-port legality:
// the second grant is impossible unless the head is granted in that cycle.
// These assertions are intended for a formal harness or an SV simulator with
// immediate assertions enabled; the module itself is combinational.
module v317_fifo_pair_reference_checks #(
    parameter integer BANK_BITS = 4
) (
    input wire head_valid,
    input wire [BANK_BITS-1:0] head_bank,
    input wire next_valid,
    input wire [BANK_BITS-1:0] next_bank,
    input wire downstream_ready
);
    wire issue_head, issue_next;
    v317_fifo_pair_reference #(.BANK_BITS(BANK_BITS)) dut (
        .head_valid(head_valid), .head_bank(head_bank),
        .next_valid(next_valid), .next_bank(next_bank),
        .downstream_ready(downstream_ready),
        .issue_head(issue_head), .issue_next(issue_next)
    );
    always @* begin
        assert (!issue_next || issue_head);
        assert (!issue_head || (head_valid && downstream_ready));
        assert (!issue_next || (next_valid && head_bank != next_bank));
        assert (!(issue_head && issue_next) || head_bank != next_bank);
        assert (issue_head == (head_valid && downstream_ready));
        assert (issue_next == (head_valid && next_valid &&
                              downstream_ready && head_bank != next_bank));
    end
endmodule
