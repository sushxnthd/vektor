module vektor_issue_control (
    input  wire         clk,
    input  wire         rst_n,
    input  wire [31:0]  wave_valid,
    input  wire [31:0]  wave_ready,
    input  wire [127:0] src0_bank_by_wave,
    input  wire [127:0] src1_bank_by_wave,
    output wire [3:0]   issue_valid,
    output wire [4:0]   issue_wave0,
    output wire [4:0]   issue_wave1,
    output wire [4:0]   issue_wave2,
    output wire [4:0]   issue_wave3
);

    wire [3:0] sched_valid;
    wire [4:0] sched_wave0;
    wire [4:0] sched_wave1;
    wire [4:0] sched_wave2;
    wire [4:0] sched_wave3;

    wire [15:0] src0_bank_flat;
    wire [15:0] src1_bank_flat;
    wire [3:0] rf_grant;
    wire [3:0] issue_accept;

    function [3:0] bank_for_wave;
        input [127:0] banks;
        input [4:0] wave_id;
        reg [127:0] shifted;
        begin
            shifted = banks >> (wave_id * 4);
            bank_for_wave = shifted[3:0];
        end
    endfunction

    assign src0_bank_flat[3:0]   = bank_for_wave(src0_bank_by_wave, sched_wave0);
    assign src0_bank_flat[7:4]   = bank_for_wave(src0_bank_by_wave, sched_wave1);
    assign src0_bank_flat[11:8]  = bank_for_wave(src0_bank_by_wave, sched_wave2);
    assign src0_bank_flat[15:12] = bank_for_wave(src0_bank_by_wave, sched_wave3);

    assign src1_bank_flat[3:0]   = bank_for_wave(src1_bank_by_wave, sched_wave0);
    assign src1_bank_flat[7:4]   = bank_for_wave(src1_bank_by_wave, sched_wave1);
    assign src1_bank_flat[11:8]  = bank_for_wave(src1_bank_by_wave, sched_wave2);
    assign src1_bank_flat[15:12] = bank_for_wave(src1_bank_by_wave, sched_wave3);

    vektor_rf_bank_arbiter rf_arbiter (
        .request_valid(sched_valid),
        .src0_bank_flat(src0_bank_flat),
        .src1_bank_flat(src1_bank_flat),
        .grant(rf_grant)
    );

    assign issue_accept = sched_valid & rf_grant;

    vektor_steal_warp_scheduler scheduler (
        .clk(clk),
        .rst_n(rst_n),
        .wave_valid(wave_valid),
        .wave_ready(wave_ready),
        .issue_accept(issue_accept),
        .issue_valid(sched_valid),
        .issue_wave0(sched_wave0),
        .issue_wave1(sched_wave1),
        .issue_wave2(sched_wave2),
        .issue_wave3(sched_wave3)
    );

    assign issue_valid = issue_accept;
    assign issue_wave0 = sched_wave0;
    assign issue_wave1 = sched_wave1;
    assign issue_wave2 = sched_wave2;
    assign issue_wave3 = sched_wave3;

endmodule
