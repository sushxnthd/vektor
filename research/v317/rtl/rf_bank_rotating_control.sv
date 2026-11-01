// V317 strong simple baseline: cyclically rotating greedy bank-port priority.
// Four slots, 16 banks, TWO independently charged reads per instruction.
// This control instantiates the existing source-faithful greedy arbiter.
// The wrapper includes its 2-bit phase state in synthesis; no free scheduler.
module vektor_v317_rf_rotating (
    input  wire        clk,
    input  wire        reset,
    input  wire [3:0]  request_valid,
    input  wire [15:0] src0_bank_flat,
    input  wire [15:0] src1_bank_flat,
    output reg  [3:0]  grant
);
    reg [1:0] phase;
    reg [3:0] valid_rot;
    reg [15:0] src0_rot;
    reg [15:0] src1_rot;
    wire [3:0] grant_rot;

    always @(posedge clk or posedge reset) begin
        if (reset)
            phase <= 2'b00;
        else
            phase <= phase + 2'b01;
    end

    // A right shift of the packed slot words places the current phase at
    // lowest priority index. No dynamic bank-port or operand forwarding.
    always @* begin
        case (phase)
            2'd0: begin
                valid_rot = request_valid;
                src0_rot = src0_bank_flat;
                src1_rot = src1_bank_flat;
            end
            2'd1: begin
                valid_rot = {request_valid[0], request_valid[3:1]};
                src0_rot = {src0_bank_flat[3:0], src0_bank_flat[15:4]};
                src1_rot = {src1_bank_flat[3:0], src1_bank_flat[15:4]};
            end
            2'd2: begin
                valid_rot = {request_valid[1:0], request_valid[3:2]};
                src0_rot = {src0_bank_flat[7:0], src0_bank_flat[15:8]};
                src1_rot = {src1_bank_flat[7:0], src1_bank_flat[15:8]};
            end
            default: begin
                valid_rot = {request_valid[2:0], request_valid[3]};
                src0_rot = {src0_bank_flat[11:0], src0_bank_flat[15:12]};
                src1_rot = {src1_bank_flat[11:0], src1_bank_flat[15:12]};
            end
        endcase
    end

    vektor_rf_bank_arbiter greedy (
        .request_valid(valid_rot),
        .src0_bank_flat(src0_rot),
        .src1_bank_flat(src1_rot),
        .grant(grant_rot)
    );

    always @* begin
        case (phase)
            2'd0: grant = grant_rot;
            2'd1: grant = {grant_rot[2:0], grant_rot[3]};
            2'd2: grant = {grant_rot[1:0], grant_rot[3:2]};
            default: grant = {grant_rot[0], grant_rot[3:1]};
        endcase
    end
endmodule
