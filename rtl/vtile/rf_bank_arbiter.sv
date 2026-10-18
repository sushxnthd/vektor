// V211: comparator-count RF arbitration. No added ports, queues, or bandwidth.
// Same fixed-priority grant semantics as vektor_rf_bank_arbiter_reference.
// Each source read contributes one token to its bank; each bank has two tokens.
module vektor_rf_bank_arbiter (
    input wire [3:0] request_valid,
    input wire [15:0] src0_bank_flat,
    input wire [15:0] src1_bank_flat,
    output wire [3:0] grant
);
    genvar i, j;
    generate for (i=0; i<4; i=i+1) begin: slot
        wire [3:0] b0 = src0_bank_flat[4*i +: 4];
        wire [3:0] b1 = src1_bank_flat[4*i +: 4];
        wire [2:0] occ0 [0:4];
        wire [2:0] occ1 [0:4];
        assign occ0[0] = 3'd0;
        assign occ1[0] = 3'd0;
        for (j=0; j<4; j=j+1) begin: prior
            if (j<i) begin: active
                wire m00 = grant[j] && (src0_bank_flat[4*j +: 4] == b0);
                wire m01 = grant[j] && (src1_bank_flat[4*j +: 4] == b0);
                wire m10 = grant[j] && (src0_bank_flat[4*j +: 4] == b1);
                wire m11 = grant[j] && (src1_bank_flat[4*j +: 4] == b1);
                assign occ0[j+1] = occ0[j] + {2'b00,m00} + {2'b00,m01};
                assign occ1[j+1] = occ1[j] + {2'b00,m10} + {2'b00,m11};
            end else begin: inactive
                assign occ0[j+1] = occ0[j];
                assign occ1[j+1] = occ1[j];
            end
        end
        assign grant[i] = request_valid[i] &&
             ((b0 == b1) ? (occ0[4] == 3'd0) :
                             ((occ0[4] < 3'd2) && (occ1[4] < 3'd2)));
    end endgenerate
endmodule

module vektor_rf_bank_arbiter_reference (
    input  wire [3:0]  request_valid,
    input  wire [15:0] src0_bank_flat,
    input  wire [15:0] src1_bank_flat,
    output reg  [3:0]  grant
);

    reg [15:0] used_once;
    reg [15:0] used_twice;
    reg [15:0] mask0;
    reg [15:0] mask1;
    integer slot;
    integer b0;
    integer b1;
    integer ok;

    always @* begin
        grant = 4'b0000;
        used_once = 16'b0;
        used_twice = 16'b0;
        mask0 = 16'b0;
        mask1 = 16'b0;
        b0 = 0;
        b1 = 0;
        ok = 0;

        for (slot = 0; slot < 4; slot = slot + 1) begin
            case (slot)
                0: begin b0 = src0_bank_flat[3:0];     b1 = src1_bank_flat[3:0];     end
                1: begin b0 = src0_bank_flat[7:4];     b1 = src1_bank_flat[7:4];     end
                2: begin b0 = src0_bank_flat[11:8];    b1 = src1_bank_flat[11:8];    end
                default: begin b0 = src0_bank_flat[15:12]; b1 = src1_bank_flat[15:12]; end
            endcase

            mask0 = 16'b1 << b0;
            mask1 = 16'b1 << b1;
            ok = 1;

            if (request_valid[slot]) begin
                if (b0 == b1) begin
                    if ((used_once & mask0) != 0)
                        ok = 0;

                    if (ok != 0) begin
                        grant[slot] = 1'b1;
                        used_once = used_once | mask0;
                        used_twice = used_twice | mask0;
                    end
                end else begin
                    if ((used_twice & mask0) != 0)
                        ok = 0;
                    if ((used_twice & mask1) != 0)
                        ok = 0;

                    if (ok != 0) begin
                        grant[slot] = 1'b1;

                        if ((used_once & mask0) != 0)
                            used_twice = used_twice | mask0;
                        else
                            used_once = used_once | mask0;

                        if ((used_once & mask1) != 0)
                            used_twice = used_twice | mask1;
                        else
                            used_once = used_once | mask1;
                    end
                end
            end
        end
    end

endmodule
