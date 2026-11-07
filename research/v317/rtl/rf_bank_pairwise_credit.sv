// V317 pairwise bank-credit implementation challenge.
// Source-faithful greedy semantics, NOT a new scheduler or extra RF ports.
// Four issue slots, 16 banks, exactly two physical reads per granted slot.
// Previous grants are counted at the operand level, including same-bank reads.
module vektor_v317_rf_pairwise (
    input  wire [3:0] request_valid,
    input  wire [15:0] src0_bank_flat,
    input  wire [15:0] src1_bank_flat,
    output wire [3:0] grant
);
    wire [3:0] bank0 [0:3];
    wire [3:0] bank1 [0:3];
    wire [3:0] admitted;

    // True when two or more earlier physical operands use one bank.
    function automatic two_or_more(input [5:0] hits);
        reg seen;
        reg twice;
        integer k;
        begin
            seen = 1'b0;
            twice = 1'b0;
            for (k = 0; k < 6; k = k + 1) begin
                twice = twice | (seen & hits[k]);
                seen = seen | hits[k];
            end
            two_or_more = twice;
        end
    endfunction

    genvar i, j;
    generate
        for (i = 0; i < 4; i = i + 1) begin : slot
            assign bank0[i] = src0_bank_flat[4*i +: 4];
            assign bank1[i] = src1_bank_flat[4*i +: 4];
            wire [5:0] earlier_on_bank0;
            wire [5:0] earlier_on_bank1;
            for (j = 0; j < 3; j = j + 1) begin : previous
                if (j < i) begin : eligible
                    assign earlier_on_bank0[2*j] =
                        admitted[j] & (bank0[j] == bank0[i]);
                    assign earlier_on_bank0[2*j+1] =
                        admitted[j] & (bank1[j] == bank0[i]);
                    assign earlier_on_bank1[2*j] =
                        admitted[j] & (bank0[j] == bank1[i]);
                    assign earlier_on_bank1[2*j+1] =
                        admitted[j] & (bank1[j] == bank1[i]);
                end else begin : unused
                    assign earlier_on_bank0[2*j] = 1'b0;
                    assign earlier_on_bank0[2*j+1] = 1'b0;
                    assign earlier_on_bank1[2*j] = 1'b0;
                    assign earlier_on_bank1[2*j+1] = 1'b0;
                end
            end
            wire same_bank = (bank0[i] == bank1[i]);
            wire permitted = same_bank
                ? ~(|earlier_on_bank0)
                : ~(two_or_more(earlier_on_bank0) |
                    two_or_more(earlier_on_bank1));
            assign admitted[i] = request_valid[i] & permitted;
        end
    endgenerate
    assign grant = admitted;
endmodule

// Equal-port rotating-priority strong control using pairwise bank credits.
// Its phase state and permutation logic are counted in matched synthesis.
module vektor_v317_rf_pairwise_rotating (
    input  wire clk,
    input  wire reset,
    input  wire [3:0] request_valid,
    input  wire [15:0] src0_bank_flat,
    input  wire [15:0] src1_bank_flat,
    output reg [3:0] grant
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

    vektor_v317_rf_pairwise core (
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
