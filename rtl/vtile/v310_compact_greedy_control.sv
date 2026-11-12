// V310 frozen strong historical matched-resource control: optimized implementation of EXISTING
// fixed-priority greedy bank admission, not a new architecture mechanism.
// Four request slots, 16 banks, two reads per request and two ports per bank.
// The same-bank dual-source request consumes BOTH ports.
// Every earlier granted request must be honored; no reordering/lookahead.
module vektor_v310_compact_greedy_arbiter (
    input wire [3:0] request_valid,
    input wire [15:0] src0_bank_flat,
    input wire [15:0] src1_bank_flat,
    output reg [3:0] grant
);
    wire [3:0] a0 = src0_bank_flat[3:0];
    wire [3:0] a1 = src0_bank_flat[7:4];
    wire [3:0] a2 = src0_bank_flat[11:8];
    wire [3:0] a3 = src0_bank_flat[15:12];
    wire [3:0] b0 = src1_bank_flat[3:0];
    wire [3:0] b1 = src1_bank_flat[7:4];
    wire [3:0] b2 = src1_bank_flat[11:8];
    wire [3:0] b3 = src1_bank_flat[15:12];

    function automatic pair_ok;
        input [3:0] ai, bi, aj, bj;
        begin
            pair_ok = !(
                ((ai == bi) && ((aj == ai) || (bj == ai))) ||
                ((aj == bj) && ((ai == aj) || (bi == aj)))
            );
        end
    endfunction

    function automatic cross3;
        input [3:0] ai, bi, aj, bj, ak, bk;
        begin
            cross3 =
                (((ai == aj) || (ai == bj)) &&
                 ((ai == ak) || (ai == bk))) ||
                (((bi == aj) || (bi == bj)) &&
                 ((bi == ak) || (bi == bk)));
        end
    endfunction

    wire p01 = pair_ok(a0,b0,a1,b1);
    wire p02 = pair_ok(a0,b0,a2,b2);
    wire p03 = pair_ok(a0,b0,a3,b3);
    wire p12 = pair_ok(a1,b1,a2,b2);
    wire p13 = pair_ok(a1,b1,a3,b3);
    wire p23 = pair_ok(a2,b2,a3,b3);
    wire c012 = cross3(a0,b0,a1,b1,a2,b2);
    wire c013 = cross3(a0,b0,a1,b1,a3,b3);
    wire c023 = cross3(a0,b0,a2,b2,a3,b3);
    wire c123 = cross3(a1,b1,a2,b2,a3,b3);

    always @* begin
        grant = 4'b0000;
        grant[0] = request_valid[0];
        grant[1] = request_valid[1] && (!grant[0] || p01);
        grant[2] = request_valid[2] &&
                   (!grant[0] || p02) && (!grant[1] || p12) &&
                   (!(grant[0] && grant[1]) || !c012);
        grant[3] = request_valid[3] &&
                   (!grant[0] || p03) && (!grant[1] || p13) &&
                   (!grant[2] || p23) &&
                   (!(grant[0] && grant[1]) || !c013) &&
                   (!(grant[0] && grant[2]) || !c023) &&
                   (!(grant[1] && grant[2]) || !c123);
    end
endmodule
