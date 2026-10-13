// V141: combinational Wave32 operand select; not an FMA or a complete collector.
// A single Wave32 writeback vector may bypass read-first RF data.
// Upstream collector/scoreboard is responsible for request persistence.
module vektor_wave32_operand_gate #(
    parameter integer LANES = 32,
    parameter integer REG_BITS = 6,
    parameter integer BYPASS = 1
) (
    input wire [3*REG_BITS-1:0] src_regs,
    input wire [2:0] pending,
    input wire [3*LANES*32-1:0] rf_values,
    input wire wb_valid,
    input wire [REG_BITS-1:0] wb_reg,
    input wire [LANES*32-1:0] wb_value,
    output wire [2:0] ready,
    output wire [2:0] rf_read,
    output wire [3*LANES*32-1:0] operands,
    output wire all_ready
);
    localparam integer WIDTH = LANES*32;
    genvar g;
    generate for (g=0;g<3;g=g+1) begin: operand
        wire hit;
        wire can_use;
        assign hit = wb_valid && (src_regs[g*REG_BITS +: REG_BITS] == wb_reg);
        if (BYPASS != 0) begin: with_forward
            assign can_use = !pending[g] || hit;
            assign rf_read[g] = !pending[g] && !hit;
            assign operands[g*WIDTH +: WIDTH] = can_use ?
                (hit ? wb_value : rf_values[g*WIDTH +: WIDTH]) : {WIDTH{1'b0}};
        end else begin: without_forward
            assign can_use = !pending[g] && !hit;
            assign rf_read[g] = can_use;
            assign operands[g*WIDTH +: WIDTH] = can_use ?
                rf_values[g*WIDTH +: WIDTH] : {WIDTH{1'b0}};
        end
        assign ready[g] = can_use;
    end endgenerate
    assign all_ready = &ready;
endmodule
