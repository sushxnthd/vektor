// V317 prospective width/slot scaling: equal-port, source-equivalent controls.
// Parameter grid S={2,4,8}, B={4,16,64}; B must be power of two.
// Both grant two reads per admitted request, maximum two reads per bank.
// This is an implementation-cost comparison, NOT a new scheduling mechanism.

module v317_bankmask_param #(
    parameter integer S = 4,
    parameter integer B = 16,
    parameter integer W = $clog2(B)
)(
    input wire [S-1:0] request_valid,
    input wire [S*W-1:0] src0_bank_flat,
    input wire [S*W-1:0] src1_bank_flat,
    output reg [S-1:0] grant
);
    reg [B-1:0] once_used, twice_used;
    reg [W-1:0] a, b;
    integer i;
    always @* begin
        grant = {S{1'b0}};
        once_used = {B{1'b0}};
        twice_used = {B{1'b0}};
        a = {W{1'b0}};
        b = {W{1'b0}};
        for (i = 0; i < S; i = i + 1) begin
            a = src0_bank_flat[i*W +: W];
            b = src1_bank_flat[i*W +: W];
            if (request_valid[i]) begin
                if (a == b) begin
                    if (!once_used[a]) begin
                        grant[i] = 1'b1;
                        once_used[a] = 1'b1;
                        twice_used[a] = 1'b1;
                    end
                end else if (!twice_used[a] && !twice_used[b]) begin
                    grant[i] = 1'b1;
                    twice_used[a] = twice_used[a] | once_used[a];
                    twice_used[b] = twice_used[b] | once_used[b];
                    once_used[a] = 1'b1;
                    once_used[b] = 1'b1;
                end
            end
        end
    end
endmodule

module v317_pairwise_param #(
    parameter integer S = 4,
    parameter integer B = 16,
    parameter integer W = $clog2(B)
)(
    input wire [S-1:0] request_valid,
    input wire [S*W-1:0] src0_bank_flat,
    input wire [S*W-1:0] src1_bank_flat,
    output reg [S-1:0] grant
);
    reg [W-1:0] a, b, prev0, prev1;
    reg seen0, twice0, seen1, twice1, hit;
    integer i, j;
    always @* begin
        grant = {S{1'b0}};
        a = {W{1'b0}};
        b = {W{1'b0}};
        prev0 = {W{1'b0}};
        prev1 = {W{1'b0}};
        seen0 = 1'b0;
        twice0 = 1'b0;
        seen1 = 1'b0;
        twice1 = 1'b0;
        hit = 1'b0;
        for (i = 0; i < S; i = i + 1) begin
            a = src0_bank_flat[i*W +: W];
            b = src1_bank_flat[i*W +: W];
            seen0 = 1'b0;
            twice0 = 1'b0;
            seen1 = 1'b0;
            twice1 = 1'b0;
            for (j = 0; j < S; j = j + 1) begin
                if ((j < i) && grant[j]) begin
                    prev0 = src0_bank_flat[j*W +: W];
                    prev1 = src1_bank_flat[j*W +: W];
                    hit = (prev0 == a);
                    twice0 = twice0 | (seen0 & hit);
                    seen0 = seen0 | hit;
                    hit = (prev1 == a);
                    twice0 = twice0 | (seen0 & hit);
                    seen0 = seen0 | hit;
                    hit = (prev0 == b);
                    twice1 = twice1 | (seen1 & hit);
                    seen1 = seen1 | hit;
                    hit = (prev1 == b);
                    twice1 = twice1 | (seen1 & hit);
                    seen1 = seen1 | hit;
                end
            end
            if (request_valid[i]) begin
                if (a == b)
                    grant[i] = !seen0;
                else
                    grant[i] = !twice0 && !twice1;
            end
        end
    end
endmodule
