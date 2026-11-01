`timescale 1ns/1ps
module tb_v317_coverage_forwarding;
    reg clk, rst_n, coverage_ok, capture_en, write_en;
    reg [1:0] cw, cb, ww, wb, rw, rb;
    reg [3:0] cr, wr, rr, captured, written, requested;
    reg [31:0] data;
    wire grant, naive_grant;
    wire [31:0] forwarded, naive_forwarded;
    integer c, r, d, lane, checks;
    reg expected;
    reg [31:0] expected_data;

    vektor_v317_coverage_forwarding dut (
        .clk(clk), .rst_n(rst_n), .coverage_ok(coverage_ok),
        .capture_en(capture_en), .capture_warp(cw),
        .capture_reg(cr), .capture_bank(cb),
        .capture_lanes(captured), .capture_data(data),
        .write_en(write_en), .write_warp(ww),
        .write_reg(wr), .write_bank(wb), .write_lanes(written),
        .requested_warp(rw), .requested_reg(rr),
        .requested_bank(rb), .requested_lanes(requested),
        .forward_grant(grant), .forwarded_data(forwarded)
    );

    vektor_v317_coverage_forwarding_naive naive_dut (
        .clk(clk), .rst_n(rst_n), .coverage_ok(coverage_ok),
        .capture_en(capture_en), .capture_warp(cw),
        .capture_reg(cr), .capture_bank(cb),
        .capture_lanes(captured), .capture_data(data),
        .write_en(write_en), .write_warp(ww),
        .write_reg(wr), .write_bank(wb), .write_lanes(written),
        .requested_warp(rw), .requested_reg(rr),
        .requested_bank(rb), .requested_lanes(requested),
        .forward_grant(naive_grant), .forwarded_data(naive_forwarded)
    );

    task tick;
        begin
            #1 clk = 1;
            #1 clk = 0;
        end
    endtask
    task check;
        input want;
        begin
            #1;
            expected_data = 0;
            for (lane = 0; lane < 4; lane = lane + 1)
                if (want && requested[lane])
                    expected_data[lane*8 +: 8] = data[lane*8 +: 8];
            if (grant !== want || forwarded !== expected_data ||
                naive_grant !== want || naive_forwarded !== expected_data)
                $fatal(1, "coverage mismatch c=%0d r=%0d d=%0d grant=%b want=%b data=%h expected=%h",
                       c, r, d, grant, want, forwarded, expected_data);
            checks = checks + 1;
        end
    endtask

    initial begin
        checks = 0; clk = 0; rst_n = 0; coverage_ok = 1;
        capture_en = 0; write_en = 0;
        cw = 0; cr = 7; cb = 2;
        ww = 0; wr = 7; wb = 2;
        rw = 0; rr = 7; rb = 2;
        captured = 0; written = 0; requested = 1;
        data = 32'h44332211;
        tick(); check(1'b0); rst_n = 1;

        // Exhaustive masks, same-cycle writes, sticky dirtiness,
        // immediate coverage loss, recovery and clean recapture.
        for (c = 0; c < 16; c = c + 1)
            for (r = 0; r < 16; r = r + 1)
                for (d = 0; d < 16; d = d + 1) begin
                    captured = c; requested = r; written = d;
                    capture_en = 1; write_en = 0;
                    tick(); capture_en = 0;
                    expected = (r != 0) && ((r & (~c & 15)) == 0);
                    check(expected);
                    write_en = 1;
                    expected = expected && ((r & d) == 0);
                    check(expected);
                    tick(); write_en = 0;
                    check(expected);
                    coverage_ok = 0;
                    check(1'b0); // combinational suppression before edge
                    tick(); coverage_ok = 1;
                    check(1'b0); // sticky after signal recovers
                    capture_en = 1; tick(); capture_en = 0;
                    expected = (r != 0) && ((r & (~c & 15)) == 0);
                    check(expected); // fresh coherent recapture
                end

        captured = 15; requested = 1; written = 0;
        capture_en = 1; coverage_ok = 0; tick();
        capture_en = 0; coverage_ok = 1; check(1'b0);
        capture_en = 1; tick(); capture_en = 0; check(1'b1);
        wr = 8; write_en = 1; written = 1;
        tick(); write_en = 0; check(1'b1);
        wr = 7; write_en = 1; check(1'b0);
        tick(); write_en = 0; check(1'b0);
        rst_n = 0; #1; check(1'b0);
        $display("V317 coverage-fail-closed RTL PASS checks=%0d", checks);
        $finish;
    end
endmodule
