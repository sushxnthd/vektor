module vektor_rf_bank_arbiter (
    input  wire [3:0]  request_valid,
    input  wire [15:0] src0_bank_flat,
    input  wire [15:0] src1_bank_flat,
    output reg  [3:0]  grant
);

    reg [2:0] reads [0:15];
    integer slot;
    integer bank;
    integer b0;
    integer b1;
    integer ok;

    always @* begin
        grant = 4'b0000;
        for (bank = 0; bank < 16; bank = bank + 1)
            reads[bank] = 3'd0;

        for (slot = 0; slot < 4; slot = slot + 1) begin
            case (slot)
                0: begin b0 = src0_bank_flat[3:0];   b1 = src1_bank_flat[3:0];   end
                1: begin b0 = src0_bank_flat[7:4];   b1 = src1_bank_flat[7:4];   end
                2: begin b0 = src0_bank_flat[11:8];  b1 = src1_bank_flat[11:8];  end
                default: begin b0 = src0_bank_flat[15:12]; b1 = src1_bank_flat[15:12]; end
            endcase

            ok = 1;
            if (request_valid[slot]) begin
                if (b0 == b1) begin
                    if ((reads[b0] + 2) > 2)
                        ok = 0;
                end else begin
                    if ((reads[b0] + 1) > 2)
                        ok = 0;
                    if ((reads[b1] + 1) > 2)
                        ok = 0;
                end

                if (ok != 0) begin
                    grant[slot] = 1'b1;
                    reads[b0] = reads[b0] + 1'b1;
                    reads[b1] = reads[b1] + 1'b1;
                end
            end
        end
    end

endmodule
