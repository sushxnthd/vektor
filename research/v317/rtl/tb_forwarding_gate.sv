\`timescale 1ns/1ps
module tb_v317_forwarding_gate;
    reg valid;
    reg [1:0] cw, cb, rw, rb;
    reg [3:0] cr, rr, captured, dirty, requested;
    reg [31:0] data;
    wire grant;
    wire [31:0] forwarded;
    integer c, r, d, lane, expected, checks;
    reg [31:0] expected_data;

    vektor_v317_forwarding_gate dut (
        .cached_valid(valid), .cached_warp(cw), .cached_reg(cr),
        .cached_bank(cb), .captured_lanes(captured),
        .dirty_lanes(dirty), .cached_data(data),
        .requested_warp(rw), .requested_reg(rr), .requested_bank(rb),
        .requested_lanes(requested), .forward_grant(grant),
        .forwarded_data(forwarded)
    );

    task verify;
        begin
            #1;
            expected = valid && (cw == rw) && (cr == rr) && (cb == rb)
                && (requested != 0) && ((requested & (~captured & 15)) == 0)
                && ((requested & dirty) == 0);
            expected_data = 0;
            for (lane = 0; lane < 4; lane = lane + 1)
                if (expected && ((requested >> lane) & 1))
                    expected_data[lane*8 +: 8] = data[lane*8 +: 8];
            if (grant !== expected[0] || forwarded !== expected_data)
                $fatal(1, "V317 forwarding mismatch c=%d r=%d d=%d", c, r, d);
            checks = checks + 1;
        end
    endtask

    initial begin
        checks = 0;
        valid = 1; cw = 0; rw = 0; cr = 7; rr = 7;
        cb = 2; rb = 2; data = 32'h44332211;
        for (c = 0; c < 16; c = c + 1)
            for (r = 0; r < 16; r = r + 1)
                for (d = 0; d < 16; d = d + 1) begin
                    captured = c; requested = r; dirty = d;
                    verify();
                end
        captured = 15; requested = 1; dirty = 0;
        rw = 1; verify(); rw = 0;
        rr = 8; verify(); rr = 7;
        rb = 1; verify(); rb = 2;
        valid = 0; verify(); valid = 1;
        dirty = 1; verify();
        dirty = 2; verify();
        $display("V317 forwarding RTL PASS checks=%0d", checks);
        $finish;
    end
endmodule
