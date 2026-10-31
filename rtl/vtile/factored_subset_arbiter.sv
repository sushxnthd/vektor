// V309 factored exact maximum-cardinality four-request bank admission.
// Same policy and tie-break as the KILLED brute-force enumerator, but without
// replicated 16-bank x 16-subset demand loops. This is a new RTL implementation
// of ONE candidate mechanism, not an additional architecture mechanism.
//
// Two source reads per request, including when both source banks are equal.
// A subset is legal iff no three selected operand occurrences share a bank.
// This follows from exactly two read ports per bank.
//
// Pair legality excludes three-equal occurrences among four pair operands.
// Triple legality adds one-from-each-request three-equal occurrences.
// Four-request legality follows from legality of all four triples.
// Ascending numerical masks within descending cardinality enforce the exact
// smallest-mask tie-break. No fairness, timing, power or workload claim.
module vektor_v309_factored_subset_arbiter (
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

    function automatic pair_legal;
        input [3:0] ai, bi, aj, bj;
        begin
            pair_legal = !(
                ((ai == bi) && ((aj == ai) || (bj == ai))) ||
                ((aj == bj) && ((ai == aj) || (bi == aj)))
            );
        end
    endfunction

    function automatic triple_cross_conflict;
        input [3:0] ai, bi, aj, bj, ak, bk;
        begin
            // Three equal operands drawn from three distinct request slots.
            triple_cross_conflict =
                (((ai == aj) || (ai == bj)) &&
                 ((ai == ak) || (ai == bk))) ||
                (((bi == aj) || (bi == bj)) &&
                 ((bi == ak) || (bi == bk)));
        end
    endfunction

    wire p01 = pair_legal(a0,b0,a1,b1);
    wire p02 = pair_legal(a0,b0,a2,b2);
    wire p03 = pair_legal(a0,b0,a3,b3);
    wire p12 = pair_legal(a1,b1,a2,b2);
    wire p13 = pair_legal(a1,b1,a3,b3);
    wire p23 = pair_legal(a2,b2,a3,b3);

    wire t012 = p01 && p02 && p12 &&
                !triple_cross_conflict(a0,b0,a1,b1,a2,b2);
    wire t013 = p01 && p03 && p13 &&
                !triple_cross_conflict(a0,b0,a1,b1,a3,b3);
    wire t023 = p02 && p03 && p23 &&
                !triple_cross_conflict(a0,b0,a2,b2,a3,b3);
    wire t123 = p12 && p13 && p23 &&
                !triple_cross_conflict(a1,b1,a2,b2,a3,b3);

    always @* begin
        // Prefer maximum cardinality; break ties by smallest numerical mask.
        grant = 4'b0000;
        if ((request_valid == 4'hf) && t012 && t013 && t023 && t123)
            grant = 4'hf;
        else if ((request_valid & 4'h7) == 4'h7 && t012)
            grant = 4'h7;
        else if ((request_valid & 4'hb) == 4'hb && t013)
            grant = 4'hb;
        else if ((request_valid & 4'hd) == 4'hd && t023)
            grant = 4'hd;
        else if ((request_valid & 4'he) == 4'he && t123)
            grant = 4'he;
        else if ((request_valid & 4'h3) == 4'h3 && p01)
            grant = 4'h3;
        else if ((request_valid & 4'h5) == 4'h5 && p02)
            grant = 4'h5;
        else if ((request_valid & 4'h6) == 4'h6 && p12)
            grant = 4'h6;
        else if ((request_valid & 4'h9) == 4'h9 && p03)
            grant = 4'h9;
        else if ((request_valid & 4'ha) == 4'ha && p13)
            grant = 4'ha;
        else if ((request_valid & 4'hc) == 4'hc && p23)
            grant = 4'hc;
        else if (request_valid[0])
            grant = 4'h1;
        else if (request_valid[1])
            grant = 4'h2;
        else if (request_valid[2])
            grant = 4'h4;
        else if (request_valid[3])
            grant = 4'h8;
    end
endmodule
