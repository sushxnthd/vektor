`timescale 1ns/1ps

module tb_rf_bank_arbiter;
    logic [3:0] request_valid;
    logic [3:0][3:0] src0_bank;
    logic [3:0][3:0] src1_bank;
    logic [3:0] grant;

    vektor_rf_bank_arbiter dut (
        .request_valid(request_valid),
        .src0_bank(src0_bank),
        .src1_bank(src1_bank),
        .grant(grant)
    );

    initial begin
        request_valid = 4'b1111;

        // No conflicts: all four instructions should be admitted.
        src0_bank[0] = 0; src1_bank[0] = 1;
        src0_bank[1] = 2; src1_bank[1] = 3;
        src0_bank[2] = 4; src1_bank[2] = 5;
        src0_bank[3] = 6; src1_bank[3] = 7;
        #1;
        if (grant !== 4'b1111)
            $fatal(1, "non-conflicting requests should all grant: %b", grant);

        // Each request consumes both read ports of bank 0; greedy priority admits one.
        src0_bank[0] = 0; src1_bank[0] = 0;
        src0_bank[1] = 0; src1_bank[1] = 0;
        src0_bank[2] = 0; src1_bank[2] = 0;
        src0_bank[3] = 0; src1_bank[3] = 0;
        #1;
        if (grant !== 4'b0001)
            $fatal(1, "same-bank double-read conflict expected 0001, got %b", grant);

        // Two instructions can each consume one bank-0 read; a third must be rejected.
        // Independent fourth instruction should still issue.
        src0_bank[0] = 0; src1_bank[0] = 1;
        src0_bank[1] = 0; src1_bank[1] = 2;
        src0_bank[2] = 0; src1_bank[2] = 3;
        src0_bank[3] = 4; src1_bank[3] = 5;
        #1;
        if (grant !== 4'b1011)
            $fatal(1, "mixed bank pressure expected 1011, got %b", grant);

        // Invalid requests consume no ports.
        request_valid = 4'b1010;
        src0_bank[1] = 7; src1_bank[1] = 7;
        src0_bank[3] = 7; src1_bank[3] = 7;
        #1;
        if (grant !== 4'b0010)
            $fatal(1, "two double-reads on one bank should admit first valid request: %b", grant);

        $display("RF bank arbiter tests passed");
        $finish;
    end
endmodule
