// V310 single active candidate: verified duplicate-operand read coalescing.
// Two ports per bank, 16 banks, four fixed-priority request slots.
// duplicate_verified[i] MUST originate from equality of complete physical
// register identities, not equality of bank indices. Defensive bank check below.
// The operand fanout datapath and physical-register comparator are not in this
// module; do not interpret its timing/area as tile-level signoff.
module vektor_v310_verified_read_coalescer (
    input wire [3:0] request_valid,
    input wire [15:0] src0_bank_flat,
    input wire [15:0] src1_bank_flat,
    input wire [3:0] duplicate_verified,
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

    // Ignore impossible duplicate assertions if the banks disagree. The
    // upstream tile must still verify full physical register identity.
    wire d0 = duplicate_verified[0] && (a0 == b0);
    wire d1 = duplicate_verified[1] && (a1 == b1);
    wire d2 = duplicate_verified[2] && (a2 == b2);
    wire d3 = duplicate_verified[3] && (a3 == b3);

    // Pair conflicts only if one request consumes BOTH ports at a bank
    // and the other request also accesses that bank.
    function automatic pair_ok;
        input [3:0] ai, bi, aj, bj;
        input di, dj;
        begin
            pair_ok = !(
                ((!di) && (ai == bi) && ((aj == ai) || (bj == ai))) ||
                ((!dj) && (aj == bj) && ((ai == aj) || (bi == aj)))
            );
        end
    endfunction

    // With pairwise safety, a three-request conflict is precisely a bank
    // touched by all three requests (one read each). This also catches
    // four-request over-subscription through three-way subsets.
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

    wire p01 = pair_ok(a0,b0,a1,b1,d0,d1);
    wire p02 = pair_ok(a0,b0,a2,b2,d0,d2);
    wire p03 = pair_ok(a0,b0,a3,b3,d0,d3);
    wire p12 = pair_ok(a1,b1,a2,b2,d1,d2);
    wire p13 = pair_ok(a1,b1,a3,b3,d1,d3);
    wire p23 = pair_ok(a2,b2,a3,b3,d2,d3);
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
