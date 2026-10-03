module vektor_fp32_fma_exact_ref (
    input  wire [31:0] a,
    input  wire [31:0] b,
    input  wire [31:0] c,
    output reg  [31:0] result,
    output reg  [4:0]  fflags
);

    // Correctness-first fused binary32 reference datapath.
    // Finite values are represented exactly on a shared 2^-298 lattice,
    // accumulated once, and rounded once to binary32 round-to-nearest-even.
    // This is deliberately not a performance microarchitecture.

    reg sign_a, sign_b, sign_c, sign_p, sign_r;
    reg [7:0] exp_a, exp_b, exp_c;
    reg [22:0] frac_a, frac_b, frac_c;
    reg nan_a, nan_b, nan_c;
    reg snan_a, snan_b, snan_c;
    reg inf_a, inf_b, inf_c;
    reg zero_a, zero_b, zero_c;
    reg invalid_op;

    reg [23:0] sig_a, sig_b, sig_c;
    reg [47:0] prod_sig;
    integer qa, qb, qc, qp;
    integer shift_p, shift_c;

    reg [555:0] prod_term;
    reg [555:0] c_term;
    reg [555:0] mag;
    reg [555:0] shifted;

    integer i;
    integer h;
    integer unbiased_exp;
    integer round_shift;
    reg guard_bit;
    reg sticky_bit;
    reg round_up;
    reg [23:0] base_sig;
    reg [24:0] rounded_sig;
    reg inexact;

    always @* begin
        result = 32'h00000000;
        fflags = 5'b00000; // {NV,DZ,OF,UF,NX}

        sign_a = a[31];
        sign_b = b[31];
        sign_c = c[31];
        sign_p = a[31] ^ b[31];
        sign_r = 1'b0;

        exp_a = a[30:23];
        exp_b = b[30:23];
        exp_c = c[30:23];
        frac_a = a[22:0];
        frac_b = b[22:0];
        frac_c = c[22:0];

        nan_a = (exp_a == 8'hff) && (frac_a != 23'b0);
        nan_b = (exp_b == 8'hff) && (frac_b != 23'b0);
        nan_c = (exp_c == 8'hff) && (frac_c != 23'b0);
        snan_a = nan_a && !frac_a[22];
        snan_b = nan_b && !frac_b[22];
        snan_c = nan_c && !frac_c[22];
        inf_a = (exp_a == 8'hff) && (frac_a == 23'b0);
        inf_b = (exp_b == 8'hff) && (frac_b == 23'b0);
        inf_c = (exp_c == 8'hff) && (frac_c == 23'b0);
        zero_a = (exp_a == 8'h00) && (frac_a == 23'b0);
        zero_b = (exp_b == 8'h00) && (frac_b == 23'b0);
        zero_c = (exp_c == 8'h00) && (frac_c == 23'b0);

        invalid_op = snan_a || snan_b || snan_c
                   || (inf_a && zero_b) || (inf_b && zero_a)
                   || ((inf_a || inf_b) && inf_c && (sign_p != sign_c));

        sig_a = 24'b0;
        sig_b = 24'b0;
        sig_c = 24'b0;
        qa = -149;
        qb = -149;
        qc = -149;
        qp = -298;
        shift_p = 0;
        shift_c = 149;
        prod_sig = 48'b0;
        prod_term = 556'b0;
        c_term = 556'b0;
        mag = 556'b0;
        shifted = 556'b0;
        h = -1;
        unbiased_exp = -1000;
        round_shift = 0;
        guard_bit = 1'b0;
        sticky_bit = 1'b0;
        round_up = 1'b0;
        base_sig = 24'b0;
        rounded_sig = 25'b0;
        inexact = 1'b0;

        if (nan_a || nan_b || nan_c || invalid_op) begin
            result = 32'h7fc00000;
            if (invalid_op)
                fflags[4] = 1'b1;
        end else if (inf_a || inf_b) begin
            result = {sign_p, 8'hff, 23'b0};
        end else if (inf_c) begin
            result = {sign_c, 8'hff, 23'b0};
        end else begin
            if (exp_a == 8'h00) begin
                sig_a = {1'b0, frac_a};
                qa = -149;
            end else begin
                sig_a = {1'b1, frac_a};
                qa = $signed({1'b0, exp_a}) - 150;
            end

            if (exp_b == 8'h00) begin
                sig_b = {1'b0, frac_b};
                qb = -149;
            end else begin
                sig_b = {1'b1, frac_b};
                qb = $signed({1'b0, exp_b}) - 150;
            end

            if (exp_c == 8'h00) begin
                sig_c = {1'b0, frac_c};
                qc = -149;
            end else begin
                sig_c = {1'b1, frac_c};
                qc = $signed({1'b0, exp_c}) - 150;
            end

            prod_sig = sig_a * sig_b;
            qp = qa + qb;
            shift_p = qp + 298;
            shift_c = qc + 298;

            if (prod_sig != 48'b0)
                prod_term = {{508{1'b0}}, prod_sig} << shift_p;
            if (sig_c != 24'b0)
                c_term = {{532{1'b0}}, sig_c} << shift_c;

            if (sign_p == sign_c) begin
                mag = prod_term + c_term;
                sign_r = sign_p;
            end else if (prod_term > c_term) begin
                mag = prod_term - c_term;
                sign_r = sign_p;
            end else if (c_term > prod_term) begin
                mag = c_term - prod_term;
                sign_r = sign_c;
            end else begin
                mag = 556'b0;
                // Exact cancellation is +0 in RNE. If both terms are zeros
                // with the same sign, preserve that common zero sign.
                if ((prod_term == 556'b0) && (c_term == 556'b0) && (sign_p == sign_c))
                    sign_r = sign_p;
                else
                    sign_r = 1'b0;
            end

            if (mag == 556'b0) begin
                result = {sign_r, 31'b0};
            end else begin
                h = -1;
                for (i = 555; i >= 0; i = i - 1) begin
                    if ((h < 0) && mag[i])
                        h = i;
                end

                unbiased_exp = h - 298;

                if (unbiased_exp > 127) begin
                    result = {sign_r, 8'hff, 23'b0};
                    fflags[2] = 1'b1; // overflow
                    fflags[0] = 1'b1; // inexact
                end else if (unbiased_exp >= -126) begin
                    round_shift = h - 23;
                    shifted = mag >> round_shift;
                    base_sig = shifted[23:0];
                    guard_bit = mag[round_shift - 1];
                    sticky_bit = 1'b0;
                    for (i = 0; i < 556; i = i + 1) begin
                        if ((i < (round_shift - 1)) && mag[i])
                            sticky_bit = 1'b1;
                    end
                    round_up = guard_bit && (sticky_bit || base_sig[0]);
                    inexact = guard_bit || sticky_bit;
                    rounded_sig = {1'b0, base_sig} + round_up;

                    if (rounded_sig[24]) begin
                        rounded_sig = rounded_sig >> 1;
                        unbiased_exp = unbiased_exp + 1;
                    end

                    if (unbiased_exp > 127) begin
                        result = {sign_r, 8'hff, 23'b0};
                        fflags[2] = 1'b1;
                        fflags[0] = 1'b1;
                    end else begin
                        result[31] = sign_r;
                        result[30:23] = unbiased_exp + 127;
                        result[22:0] = rounded_sig[22:0];
                        if (inexact)
                            fflags[0] = 1'b1;
                    end
                end else begin
                    // Every binary32 subnormal is an integer multiple of
                    // 2^-149. The exact accumulator is in units of 2^-298,
                    // so subnormal rounding always discards exactly 149 bits.
                    shifted = mag >> 149;
                    base_sig = shifted[23:0];
                    guard_bit = mag[148];
                    sticky_bit = |mag[147:0];
                    round_up = guard_bit && (sticky_bit || base_sig[0]);
                    inexact = guard_bit || sticky_bit;
                    rounded_sig = {1'b0, base_sig} + round_up;

                    if (rounded_sig[23]) begin
                        // Rounded across the subnormal/normal boundary.
                        result = {sign_r, 8'h01, 23'b0};
                    end else begin
                        result = {sign_r, 8'h00, rounded_sig[22:0]};
                        if (inexact)
                            fflags[1] = 1'b1; // tininess after rounding + inexact
                    end
                    if (inexact)
                        fflags[0] = 1'b1;
                end
            end
        end
    end

endmodule
