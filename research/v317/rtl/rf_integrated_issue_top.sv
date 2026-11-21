// V317 integrated 32-wave issue-control physicality experiment.
// Source path instantiates unmodified rtl/vtile/issue_control.sv.
// Pairwise path copies only its interconnect and swaps the grant-equivalent arbiter.
// No new scheduling policy, register-file read ports, SRAM, or datapath are added.
module vektor_v317_issue_control_pairwise (
    input wire clk,
    input wire rst_n,
    input wire [31:0] wave_valid,
    input wire [31:0] wave_ready,
    input wire [127:0] src0_bank_by_wave,
    input wire [127:0] src1_bank_by_wave,
    output wire [3:0] issue_valid,
    output wire [4:0] issue_wave0,
    output wire [4:0] issue_wave1,
    output wire [4:0] issue_wave2,
    output wire [4:0] issue_wave3
);
    wire [3:0] sched_valid;
    wire [4:0] sched_wave0, sched_wave1, sched_wave2, sched_wave3;
    wire [15:0] src0_bank_flat, src1_bank_flat;
    wire [3:0] rf_grant, issue_accept;

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

    vektor_v317_rf_pairwise rf_arbiter (
        .request_valid(sched_valid),
        .src0_bank_flat(src0_bank_flat),
        .src1_bank_flat(src1_bank_flat),
        .grant(rf_grant)
    );
    assign issue_accept = sched_valid & rf_grant;

    vektor_steal_warp_scheduler scheduler (
        .clk(clk), .rst_n(rst_n),
        .wave_valid(wave_valid), .wave_ready(wave_ready),
        .issue_accept(issue_accept), .issue_valid(sched_valid),
        .issue_wave0(sched_wave0), .issue_wave1(sched_wave1),
        .issue_wave2(sched_wave2), .issue_wave3(sched_wave3)
    );

    assign issue_valid = issue_accept;
    assign issue_wave0 = sched_wave0;
    assign issue_wave1 = sched_wave1;
    assign issue_wave2 = sched_wave2;
    assign issue_wave3 = sched_wave3;
endmodule

module vektor_v317_issue_integrated_core #(
    parameter USE_PAIRWISE = 0
) (
    input wire clk,
    input wire rst_n,
    input wire [31:0] wave_valid,
    input wire [31:0] wave_ready,
    input wire [127:0] src0_bank_by_wave,
    input wire [127:0] src1_bank_by_wave,
    output reg [3:0] issue_valid_q,
    output reg [19:0] issue_wave_flat_q
);
    reg [31:0] valid_q, ready_q;
    reg [127:0] bank0_q, bank1_q;
    wire [3:0] issue_valid;
    wire [4:0] wave0, wave1, wave2, wave3;

    always @(posedge clk) begin
        valid_q <= wave_valid;
        ready_q <= wave_ready;
        bank0_q <= src0_bank_by_wave;
        bank1_q <= src1_bank_by_wave;
        issue_valid_q <= issue_valid;
        issue_wave_flat_q <= {wave3, wave2, wave1, wave0};
    end

    generate if (USE_PAIRWISE != 0) begin : pairwise
        vektor_v317_issue_control_pairwise issue (
            .clk(clk), .rst_n(rst_n),
            .wave_valid(valid_q), .wave_ready(ready_q),
            .src0_bank_by_wave(bank0_q), .src1_bank_by_wave(bank1_q),
            .issue_valid(issue_valid), .issue_wave0(wave0), .issue_wave1(wave1),
            .issue_wave2(wave2), .issue_wave3(wave3)
        );
    end else begin : original
        vektor_issue_control issue (
            .clk(clk), .rst_n(rst_n),
            .wave_valid(valid_q), .wave_ready(ready_q),
            .src0_bank_by_wave(bank0_q), .src1_bank_by_wave(bank1_q),
            .issue_valid(issue_valid), .issue_wave0(wave0), .issue_wave1(wave1),
            .issue_wave2(wave2), .issue_wave3(wave3)
        );
    end endgenerate
endmodule

module vektor_v317_issue_integrated_top_source (
    input wire clk, input wire rst_n,
    input wire [31:0] wave_valid, wave_ready,
    input wire [127:0] src0_bank_by_wave, src1_bank_by_wave,
    output wire [3:0] issue_valid_q,
    output wire [19:0] issue_wave_flat_q
);
    vektor_v317_issue_integrated_core #(.USE_PAIRWISE(0)) core (
        .clk(clk), .rst_n(rst_n), .wave_valid(wave_valid), .wave_ready(wave_ready),
        .src0_bank_by_wave(src0_bank_by_wave), .src1_bank_by_wave(src1_bank_by_wave),
        .issue_valid_q(issue_valid_q), .issue_wave_flat_q(issue_wave_flat_q)
    );
endmodule

module vektor_v317_issue_integrated_top_pairwise (
    input wire clk, input wire rst_n,
    input wire [31:0] wave_valid, wave_ready,
    input wire [127:0] src0_bank_by_wave, src1_bank_by_wave,
    output wire [3:0] issue_valid_q,
    output wire [19:0] issue_wave_flat_q
);
    vektor_v317_issue_integrated_core #(.USE_PAIRWISE(1)) core (
        .clk(clk), .rst_n(rst_n), .wave_valid(wave_valid), .wave_ready(wave_ready),
        .src0_bank_by_wave(src0_bank_by_wave), .src1_bank_by_wave(src1_bank_by_wave),
        .issue_valid_q(issue_valid_q), .issue_wave_flat_q(issue_wave_flat_q)
    );
endmodule
