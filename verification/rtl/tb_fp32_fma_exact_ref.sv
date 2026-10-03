`timescale 1ns/1ps

module tb_fp32_fma_exact_ref;
    logic [31:0] a;
    logic [31:0] b;
    logic [31:0] c;
    logic [31:0] result;
    logic [4:0] fflags;

    integer fd;
    integer rc;
    integer count;
    reg [31:0] va;
    reg [31:0] vb;
    reg [31:0] vc;
    reg [31:0] expected;

    vektor_fp32_fma_exact_ref dut (
        .a(a),
        .b(b),
        .c(c),
        .result(result),
        .fflags(fflags)
    );

    task check_case(
        input [31:0] ta,
        input [31:0] tb,
        input [31:0] tc,
        input [31:0] tr,
        input [4:0] tf
    );
        begin
            a = ta;
            b = tb;
            c = tc;
            #1;
            if (result !== tr)
                $fatal(1, "result mismatch: a=%08x b=%08x c=%08x got=%08x expected=%08x", ta, tb, tc, result, tr);
            if (fflags !== tf)
                $fatal(1, "fflags mismatch: a=%08x b=%08x c=%08x got=%05b expected=%05b", ta, tb, tc, fflags, tf);
        end
    endtask

    initial begin
        a = 32'b0;
        b = 32'b0;
        c = 32'b0;

        fd = $fopen("build/rtl/fmaf_vectors.txt", "r");
        if (fd == 0)
            $fatal(1, "unable to open build/rtl/fmaf_vectors.txt");

        count = 0;
        while (!$feof(fd)) begin
            rc = $fscanf(fd, "%h %h %h %h\n", va, vb, vc, expected);
            if (rc == 4) begin
                a = va;
                b = vb;
                c = vc;
                #1;
                if (result !== expected)
                    $fatal(1, "vector %0d mismatch: a=%08x b=%08x c=%08x got=%08x expected=%08x flags=%05b",
                        count, va, vb, vc, result, expected, fflags);
                count = count + 1;
            end
        end
        $fclose(fd);

        if (count < 10000)
            $fatal(1, "expected at least 10000 fused vectors, saw %0d", count);

        // Signaling NaN sets invalid and canonicalizes the result.
        check_case(32'h7f800001, 32'h3f800000, 32'h00000000,
                   32'h7fc00000, 5'b10000);

        // Infinity times zero is invalid.
        check_case(32'h7f800000, 32'h00000000, 32'h00000000,
                   32'h7fc00000, 5'b10000);

        // Finite overflow: +max * 2 + 0 -> +inf, overflow + inexact.
        check_case(32'h7f7fffff, 32'h40000000, 32'h00000000,
                   32'h7f800000, 5'b00101);

        // Exact smallest subnormal survives without underflow/inexact.
        check_case(32'h00000001, 32'h3f800000, 32'h00000000,
                   32'h00000001, 5'b00000);

        // Half a minimum subnormal is exactly halfway and rounds to even zero.
        check_case(32'h00000001, 32'h3f000000, 32'h00000000,
                   32'h00000000, 5'b00011);

        // Exact cancellation in RNE produces +0.
        check_case(32'h3f800000, 32'h3f800000, 32'hbf800000,
                   32'h00000000, 5'b00000);

        // Same-sign negative zero is preserved.
        check_case(32'h80000000, 32'h3f800000, 32'h80000000,
                   32'h80000000, 5'b00000);

        $display("fp32 exact FMA tests passed: %0d glibc-fmaf vectors + directed flags", count);
        $finish;
    end
endmodule
