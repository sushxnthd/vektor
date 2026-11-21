`timescale 1ns/1ps
module tb_v317_dual_write_forwarding;
    reg clk, rst_n, coverage_ok, capture_en, write0_en, write1_en;
    reg [1:0] cw, cb, rw, rb, w0w, w0b, w1w, w1b;
    reg [3:0] cr, rr, w0r, w1r, captured, requested, w0mask, w1mask;
    reg [31:0] data;
    wire dual_grant, single_grant;
    wire [31:0] dual_data, single_data;
    integer c, r, d, e, lane, checks;
    reg want;
    reg [31:0] expected_data;

    vektor_v317_dual_write_forwarding dut (
        .clk(clk), .rst_n(rst_n), .coverage_ok(coverage_ok),
        .capture_en(capture_en), .capture_warp(cw), .capture_reg(cr),
        .capture_bank(cb), .capture_lanes(captured), .capture_data(data),
        .write0_en(write0_en), .write0_warp(w0w), .write0_reg(w0r),
        .write0_bank(w0b), .write0_lanes(w0mask),
        .write1_en(write1_en), .write1_warp(w1w), .write1_reg(w1r),
        .write1_bank(w1b), .write1_lanes(w1mask),
        .requested_warp(rw), .requested_reg(rr), .requested_bank(rb),
        .requested_lanes(requested), .forward_grant(dual_grant),
        .forwarded_data(dual_data)
    );
    // Negative integration control: this model sees only port 0.
    vektor_v317_coverage_forwarding single_port (
        .clk(clk), .rst_n(rst_n), .coverage_ok(coverage_ok),
        .capture_en(capture_en), .capture_warp(cw), .capture_reg(cr),
        .capture_bank(cb), .capture_lanes(captured), .capture_data(data),
        .write_en(write0_en), .write_warp(w0w), .write_reg(w0r),
        .write_bank(w0b), .write_lanes(w0mask),
        .requested_warp(rw), .requested_reg(rr), .requested_bank(rb),
        .requested_lanes(requested), .forward_grant(single_grant),
        .forwarded_data(single_data)
    );

    task tick;
        begin #1 clk = 1; #1 clk = 0; end
    endtask
    task check;
        input expected;
        begin
            #1;
            expected_data = 0;
            for (lane = 0; lane < 4; lane = lane + 1)
                if (expected && requested[lane])
                    expected_data[lane*8 +: 8] = data[lane*8 +: 8];
            if (dual_grant !== expected || dual_data !== expected_data)
                $fatal(1, "dual-port mismatch c=%0d r=%0d d=%0d e=%0d got=%b/%h want=%b/%h",
                    c,r,d,e,dual_grant,dual_data,expected,expected_data);
            checks = checks + 1;
        end
    endtask
    initial begin
        checks = 0; clk = 0; rst_n = 0; coverage_ok = 1;
        capture_en = 0; write0_en = 0; write1_en = 0;
        cw = 0; cr = 7; cb = 2; rw = 0; rr = 7; rb = 2;
        w0w = 0; w0r = 7; w0b = 2; w1w = 0; w1r = 7; w1b = 2;
        captured = 15; requested = 1; w0mask = 0; w1mask = 0;
        data = 32'h44332211;
        tick(); check(1'b0); rst_n = 1;

        // Full Cartesian mask sweep: 16^4 configurations, two live ports,
        // sticky union, immediate fault, and recovery.
        for (c = 0; c < 16; c = c + 1)
            for (r = 0; r < 16; r = r + 1)
                for (d = 0; d < 16; d = d + 1)
                    for (e = 0; e < 16; e = e + 1) begin
                        captured = c; requested = r;
                        w0mask = d; w1mask = e;
                        capture_en = 1; write0_en = 0; write1_en = 0;
                        tick(); capture_en = 0;
                        want = (r != 0) && ((r & (~c & 15)) == 0);
                        check(want);
                        write0_en = 1; write1_en = 1;
                        want = want && ((r & (d | e)) == 0);
                        check(want);
                        tick(); write0_en = 0; write1_en = 0;
                        check(want);
                        coverage_ok = 0; check(1'b0);
                        tick(); coverage_ok = 1; check(1'b0);
                        capture_en = 1; tick(); capture_en = 0;
                        want = (r != 0) && ((r & (~c & 15)) == 0);
                        check(want);
                    end

        // Namespace separation: neither wrong-register nor wrong-warp writes
        // may poison a snapshot, even with full lane masks.
        captured = 15; requested = 1; w0mask = 15; w1mask = 15;
        write0_en = 0; write1_en = 0;
        capture_en = 1; tick(); capture_en = 0; check(1'b1);
        w0r = 8; w1w = 1; write0_en = 1; write1_en = 1;
        check(1'b1); tick(); check(1'b1);
        write0_en = 0; write1_en = 0; w0r = 7; w1w = 0;

        // Both ports overlap a simultaneous capture; fail closed.
        w0mask = 1; w1mask = 2; requested = 3;
        write0_en = 1; write1_en = 1; capture_en = 1;
        tick(); capture_en = 0; write0_en = 0; write1_en = 0;
        check(1'b0);
        capture_en = 1; tick(); capture_en = 0;
        check(1'b1);

        // Actual counterexample to naive integration of the one-port RTL:
        // port 1 changes lane 0 while port 0 is idle. One-port model
        // admits a stale snapshot, dual-port model rejects it.
        requested = 1; w1mask = 1;
        write0_en = 0; write1_en = 1;
        check(1'b0);
        if (single_grant !== 1'b1 || single_data !== 32'h00000011)
            $fatal(1, "expected stale one-port integration witness absent");
        tick(); write1_en = 0;
        check(1'b0);
        if (single_grant !== 1'b1)
            $fatal(1, "one-port model did not retain stale admission");
        rst_n = 0; #1; check(1'b0);
        $display("V317 dual-write completeness PASS checks=%0d", checks);
        $finish;
    end
endmodule
