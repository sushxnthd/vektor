`timescale 1ns/1ps

module tb_rf_bank_arbiter;
    logic [3:0] request_valid;
    logic [15:0] src0_bank_flat;
    logic [15:0] src1_bank_flat;
    logic [3:0] grant;

    vektor_rf_bank_arbiter dut (
        .request_valid(request_valid),
        .src0_bank_flat(src0_bank_flat),
        .src1_bank_flat(src1_bank_flat),
        .grant(grant)
    );

    task set_banks(
        input [3:0] a0, input [3:0] a1,
        input [3:0] b0, input [3:0] b1,
        input [3:0] c0, input [3:0] c1,
        input [3:0] d0, input [3:0] d1
    );
        begin
            src0_bank_flat = {d0, c0, b0, a0};
            src1_bank_flat = {d1, c1, b1, a1};
        end
    endtask

    initial begin
        request_valid = 4'b1111;

        set_banks(0,1, 2,3, 4,5, 6,7);
        #1;
        if (grant !== 4'b1111)
            $fatal(1, "non-conflicting requests should all grant: %b", grant);

        set_banks(0,0, 0,0, 0,0, 0,0);
        #1;
        if (grant !== 4'b0001)
            $fatal(1, "same-bank double-read conflict expected 0001, got %b", grant);

        set_banks(0,1, 0,2, 0,3, 4,5);
        #1;
        if (grant !== 4'b1011)
            $fatal(1, "mixed bank pressure expected 1011, got %b", grant);

        request_valid = 4'b1010;
        set_banks(0,0, 7,7, 0,0, 7,7);
        #1;
        if (grant !== 4'b0010)
            $fatal(1, "two double-reads on one bank should admit first valid request: %b", grant);

        $display("RF bank arbiter tests passed");
        $finish;
    end
endmodule
