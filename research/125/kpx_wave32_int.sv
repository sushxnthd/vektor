// Vektor-125: executable KPX-0 Wave32 integer/predication slice.
// Scope: one issue/cycle functional contract, NOT a timing-closed GPU tile.
// No load/store, FP32, texture, matrix, or inter-wave operations implemented.
// Copyright (c) Vektor contributors. Original, synthesizable SystemVerilog.
module kpx_wave32_int #(
    parameter integer WAVE = 32,
    parameter integer REGS = 16,
    parameter integer STACK = 8
)(
    input  wire clk,
    input  wire rst_n,                  // synchronous active-low reset
    input  wire [WAVE-1:0] initial_mask_i,
    input  wire valid_i,
    input  wire [3:0] opcode_i,
    input  wire [3:0] rd_i,
    input  wire [3:0] rs1_i,
    input  wire [3:0] rs2_i,
    input  wire [31:0] imm_i,
    output wire ready_o,
    output wire fault_o,
    output wire commit_o,
    output wire [WAVE-1:0] mask_o,
    output wire [3:0] depth_o,
    input  wire [3:0] dbg_reg_i,
    input  wire [4:0] dbg_lane_i,
    output wire [31:0] dbg_value_o
);
    localparam [3:0] OP_LANEID=4'd0, OP_IMM=4'd1,
                     OP_ADD=4'd2, OP_MUL=4'd3, OP_XOR=4'd4,
                     OP_IFLT=4'd5, OP_ELSE=4'd6, OP_ENDIF=4'd7,
                     OP_BALLOT=4'd8, OP_REDUCE=4'd9;
    reg [31:0] rf [0:REGS-1][0:WAVE-1];
    reg [WAVE-1:0] mask_q;
    reg [WAVE-1:0] stack_parent [0:STACK-1];
    reg [WAVE-1:0] stack_cond [0:STACK-1];
    reg stack_else [0:STACK-1];
    reg [3:0] depth_q;
    reg [WAVE-1:0] cmp_mask;
    reg [WAVE-1:0] ballot;
    reg [31:0] reduction;
    integer i, j;
    always @* begin
        cmp_mask = {WAVE{1'b0}};
        ballot = {WAVE{1'b0}};
        reduction = 32'b0;
        for (integer k=0; k<WAVE; k=k+1) begin
            if (mask_q[k]) begin
                if (rf[rs1_i][k] < rf[rs2_i][k]) cmp_mask[k] = 1'b1;
                if (rf[rs1_i][k] != 32'b0) ballot[k] = 1'b1;
                reduction = reduction + rf[rs1_i][k];
            end
        end
    end
    assign ready_o = 1'b1;
    assign fault_o = valid_i && ((opcode_i > OP_REDUCE) ||
                      (opcode_i == OP_IFLT && depth_q == STACK) ||
                      (opcode_i == OP_ELSE &&
                          (depth_q == 0 || (depth_q != 0 && stack_else[depth_q-1'b1]))) ||
                      (opcode_i == OP_ENDIF && depth_q == 0));
    assign commit_o = valid_i && !fault_o;
    assign mask_o = mask_q;
    assign depth_o = depth_q;
    assign dbg_value_o = rf[dbg_reg_i][dbg_lane_i];

    always @(posedge clk) begin
        if (!rst_n) begin
            mask_q <= initial_mask_i;
            depth_q <= 0;
            for (i=0; i<REGS; i=i+1)
                for (j=0; j<WAVE; j=j+1) rf[i][j] <= 32'b0;
            for (i=0; i<STACK; i=i+1) begin
                stack_parent[i] <= {WAVE{1'b0}};
                stack_cond[i] <= {WAVE{1'b0}};
                stack_else[i] <= 1'b0;
            end
        end else if (commit_o) begin
            case (opcode_i)
                OP_IFLT: begin
                    stack_parent[depth_q] <= mask_q;
                    stack_cond[depth_q] <= cmp_mask;
                    stack_else[depth_q] <= 1'b0;
                    depth_q <= depth_q + 1'b1;
                    mask_q <= cmp_mask;
                end
                OP_ELSE: begin
                    stack_else[depth_q-1'b1] <= 1'b1;
                    mask_q <= stack_parent[depth_q-1'b1] & ~stack_cond[depth_q-1'b1];
                end
                OP_ENDIF: begin
                    mask_q <= stack_parent[depth_q-1'b1];
                    depth_q <= depth_q - 1'b1;
                end
                default: begin
                    for (i=0; i<WAVE; i=i+1) begin
                        if (mask_q[i]) begin
                            case (opcode_i)
                                OP_LANEID: rf[rd_i][i] <= i;
                                OP_IMM: rf[rd_i][i] <= imm_i;
                                OP_ADD: rf[rd_i][i] <= rf[rs1_i][i] + rf[rs2_i][i];
                                OP_MUL: rf[rd_i][i] <= rf[rs1_i][i] * rf[rs2_i][i];
                                OP_XOR: rf[rd_i][i] <= rf[rs1_i][i] ^ rf[rs2_i][i];
                                OP_BALLOT: rf[rd_i][i] <= ballot;
                                OP_REDUCE: rf[rd_i][i] <= reduction;
                                default: ;
                            endcase
                        end
                    end
                end
            endcase
        end
    end
endmodule
