// V317 physicality challenge: matched 16-bank dual-read flop RF proxy.
// This is NOT an SRAM macro or GPU tile. Each bank has exactly two read ports.
// Both variants share this unchanged storage, port selection, and operand sink.
module vektor_v317_rf_proxy_16b_2r (
    input wire clk,
    input wire wr_en,
    input wire [3:0] wr_bank,
    input wire [1:0] wr_row,
    input wire [7:0] wr_data,
    input wire [3:0] issue_valid,
    input wire [19:0] issue_wave_flat,
    input wire [127:0] bank0_by_wave,
    input wire [127:0] bank1_by_wave,
    output wire [63:0] operand_data,
    output wire bank_port_overflow
);
    function [3:0] bank_for_wave;
        input [127:0] banks;
        input [4:0] wave;
        reg [127:0] shifted;
        begin
            shifted = banks >> (wave * 4);
            bank_for_wave = shifted[3:0];
        end
    endfunction

    wire [3:0] operand_bank [0:7];
    wire [1:0] operand_row [0:7];
    wire [7:0] operand_valid;
    genvar s, b, o;
    generate for (s = 0; s < 4; s = s + 1) begin : operand_request
        assign operand_bank[2*s] = bank_for_wave(bank0_by_wave, issue_wave_flat[5*s +: 5]);
        assign operand_bank[2*s+1] = bank_for_wave(bank1_by_wave, issue_wave_flat[5*s +: 5]);
        assign operand_row[2*s] = issue_wave_flat[5*s +: 2];
        assign operand_row[2*s+1] = issue_wave_flat[5*s+2 +: 2];
        assign operand_valid[2*s] = issue_valid[s];
        assign operand_valid[2*s+1] = issue_valid[s];
    end endgenerate

    wire [7:0] read0 [0:15];
    wire [7:0] read1 [0:15];
    wire [2:0] lane0 [0:15];
    wire [2:0] lane1 [0:15];
    wire has0 [0:15];
    wire has1 [0:15];
    wire [15:0] overflow;
    generate for (b = 0; b < 16; b = b + 1) begin : bank
        localparam [3:0] BANK_ID = b;
        reg [7:0] words [0:3];
        reg [2:0] select0, select1;
        reg [1:0] addr0, addr1;
        reg valid0, valid1, excess;
        integer k;
        always @(posedge clk)
            if (wr_en && wr_bank == BANK_ID)
                words[wr_row] <= wr_data;
        always @* begin
            select0 = 0;
            select1 = 0;
            addr0 = 0;
            addr1 = 0;
            valid0 = 0;
            valid1 = 0;
            excess = 0;
            for (k = 0; k < 8; k = k + 1) begin
                if (operand_valid[k] && operand_bank[k] == BANK_ID) begin
                    if (!valid0) begin
                        valid0 = 1;
                        select0 = k;
                        addr0 = operand_row[k];
                    end else if (!valid1) begin
                        valid1 = 1;
                        select1 = k;
                        addr1 = operand_row[k];
                    end else begin
                        excess = 1;
                    end
                end
            end
        end
        assign read0[b] = words[addr0];
        assign read1[b] = words[addr1];
        assign lane0[b] = select0;
        assign lane1[b] = select1;
        assign has0[b] = valid0;
        assign has1[b] = valid1;
        assign overflow[b] = excess;
    end endgenerate

    generate for (o = 0; o < 8; o = o + 1) begin : operand_response
        wire [3:0] which_bank = operand_bank[o];
        assign operand_data[8*o +: 8] =
            !operand_valid[o] ? 8'b0 :
            (has0[which_bank] && lane0[which_bank] == o) ? read0[which_bank] :
            (has1[which_bank] && lane1[which_bank] == o) ? read1[which_bank] :
            8'b0;
    end endgenerate
    assign bank_port_overflow = |overflow;
endmodule

module vektor_v317_rf_proxy_integrated_core #(
    parameter USE_PAIRWISE = 0
) (
    input wire clk, rst_n,
    input wire [31:0] wave_valid, wave_ready,
    input wire [127:0] src0_bank_by_wave, src1_bank_by_wave,
    input wire wr_en,
    input wire [3:0] wr_bank,
    input wire [1:0] wr_row,
    input wire [7:0] wr_data,
    output reg [3:0] issue_valid_sink_q,
    output reg [19:0] issue_wave_sink_q,
    output reg [63:0] operands_q,
    output reg overflow_q
);
    wire [3:0] issue_valid_q;
    wire [19:0] issue_wave_q;
    reg [127:0] bank0_d0, bank0_d1, bank1_d0, bank1_d1;
    wire [63:0] operands;
    wire overflow;

    vektor_v317_issue_integrated_core #(.USE_PAIRWISE(USE_PAIRWISE)) issue_core (
        .clk(clk), .rst_n(rst_n),
        .wave_valid(wave_valid), .wave_ready(wave_ready),
        .src0_bank_by_wave(src0_bank_by_wave),
        .src1_bank_by_wave(src1_bank_by_wave),
        .issue_valid_q(issue_valid_q),
        .issue_wave_flat_q(issue_wave_q)
    );
    // The issue core captures bank inputs, then registers grants one cycle later.
    // Two input delays align bank tags with the issued wave IDs at the RF read.
    always @(posedge clk) begin
        bank0_d0 <= src0_bank_by_wave;
        bank1_d0 <= src1_bank_by_wave;
        bank0_d1 <= bank0_d0;
        bank1_d1 <= bank1_d0;
        issue_valid_sink_q <= issue_valid_q;
        issue_wave_sink_q <= issue_wave_q;
        operands_q <= operands;
        overflow_q <= overflow;
    end
    vektor_v317_rf_proxy_16b_2r rf (
        .clk(clk), .wr_en(wr_en), .wr_bank(wr_bank),
        .wr_row(wr_row), .wr_data(wr_data),
        .issue_valid(issue_valid_q), .issue_wave_flat(issue_wave_q),
        .bank0_by_wave(bank0_d1), .bank1_by_wave(bank1_d1),
        .operand_data(operands), .bank_port_overflow(overflow)
    );
endmodule

module vektor_v317_rf_proxy_top_source (
    input wire clk, rst_n,
    input wire [31:0] wave_valid, wave_ready,
    input wire [127:0] src0_bank_by_wave, src1_bank_by_wave,
    input wire wr_en, input wire [3:0] wr_bank,
    input wire [1:0] wr_row, input wire [7:0] wr_data,
    output wire [3:0] issue_valid_sink_q,
    output wire [19:0] issue_wave_sink_q,
    output wire [63:0] operands_q,
    output wire overflow_q
);
    vektor_v317_rf_proxy_integrated_core #(.USE_PAIRWISE(0)) core (
        .clk(clk), .rst_n(rst_n),
        .wave_valid(wave_valid), .wave_ready(wave_ready),
        .src0_bank_by_wave(src0_bank_by_wave), .src1_bank_by_wave(src1_bank_by_wave),
        .wr_en(wr_en), .wr_bank(wr_bank), .wr_row(wr_row), .wr_data(wr_data),
        .issue_valid_sink_q(issue_valid_sink_q),
        .issue_wave_sink_q(issue_wave_sink_q),
        .operands_q(operands_q), .overflow_q(overflow_q)
    );
endmodule

module vektor_v317_rf_proxy_top_pairwise (
    input wire clk, rst_n,
    input wire [31:0] wave_valid, wave_ready,
    input wire [127:0] src0_bank_by_wave, src1_bank_by_wave,
    input wire wr_en, input wire [3:0] wr_bank,
    input wire [1:0] wr_row, input wire [7:0] wr_data,
    output wire [3:0] issue_valid_sink_q,
    output wire [19:0] issue_wave_sink_q,
    output wire [63:0] operands_q,
    output wire overflow_q
);
    vektor_v317_rf_proxy_integrated_core #(.USE_PAIRWISE(1)) core (
        .clk(clk), .rst_n(rst_n),
        .wave_valid(wave_valid), .wave_ready(wave_ready),
        .src0_bank_by_wave(src0_bank_by_wave), .src1_bank_by_wave(src1_bank_by_wave),
        .wr_en(wr_en), .wr_bank(wr_bank), .wr_row(wr_row), .wr_data(wr_data),
        .issue_valid_sink_q(issue_valid_sink_q),
        .issue_wave_sink_q(issue_wave_sink_q),
        .operands_q(operands_q), .overflow_q(overflow_q)
    );
endmodule
