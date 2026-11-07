`timescale 1ns/1ps
module tb_rf_registered_physical;
    reg clk = 0;
    always #5 clk = ~clk;
    reg [3:0] request_valid = 0;
    reg [15:0] src0_bank_flat = 0;
    reg [15:0] src1_bank_flat = 0;
    wire [3:0] source_grant, pairwise_grant;
    integer i;
    vektor_v317_rf_physical_top_source source_dut (
        .clk(clk), .request_valid(request_valid),
        .src0_bank_flat(src0_bank_flat), .src1_bank_flat(src1_bank_flat),
        .grant(source_grant)
    );
    vektor_v317_rf_physical_top_pairwise pairwise_dut (
        .clk(clk), .request_valid(request_valid),
        .src0_bank_flat(src0_bank_flat), .src1_bank_flat(src1_bank_flat),
        .grant(pairwise_grant)
    );
    initial begin
        // First two cycles fill the identical two-stage register boundary.
        for (i = 0; i < 5000; i = i + 1) begin
            @(negedge clk);
            request_valid = $random;
            src0_bank_flat = $random;
            src1_bank_flat = $random;
            @(posedge clk);
            #1;
            if (i > 1 && source_grant !== pairwise_grant) begin
                $display("FAIL cycle=%0d source=%b pairwise=%b", i, source_grant, pairwise_grant);
                $fatal(1);
            end
        end
        $display("PASS: 4998 post-fill registered source/pairwise comparisons");
        $finish;
    end
endmodule
