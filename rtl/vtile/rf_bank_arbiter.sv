// V203: source-alias RF port compaction. Equal bank/port/queue budget.
// src_alias[i] may be set only if the two operands have identical physical
// register identity in the same wave. RF data must fan to both operand latches.
module vektor_rf_bank_arbiter (
    input wire [3:0] request_valid,
    input wire [15:0] src0_bank_flat,
    input wire [15:0] src1_bank_flat,
    input wire [3:0] src_alias,
    output reg [3:0] grant
);
    reg [15:0] used_once, used_twice, mask0, mask1;
    integer slot, b0, b1;
    reg ok, alias_read;
    always @* begin
        grant = 4'b0000;
        used_once = 16'b0;
        used_twice = 16'b0;
        mask0 = 16'b0;
        mask1 = 16'b0;
        b0 = 0;
        b1 = 0;
        ok = 1'b0;
        alias_read = 1'b0;
        for (slot = 0; slot < 4; slot = slot + 1) begin
            b0 = src0_bank_flat[4*slot +: 4];
            b1 = src1_bank_flat[4*slot +: 4];
            mask0 = 16'b1 << b0;
            mask1 = 16'b1 << b1;
            alias_read = src_alias[slot] && (b0 == b1);
            ok = 1'b1;
            if (request_valid[slot]) begin
                if (b0 == b1) begin
                    if (alias_read) begin
                        if ((used_twice & mask0) != 0) ok = 1'b0;
                    end else if ((used_once & mask0) != 0) ok = 1'b0;
                    if (ok) begin
                        grant[slot] = 1'b1;
                        if (alias_read) begin
                            if ((used_once & mask0) != 0)
                                used_twice = used_twice | mask0;
                            else
                                used_once = used_once | mask0;
                        end else begin
                            used_once = used_once | mask0;
                            used_twice = used_twice | mask0;
                        end
                    end
                end else begin
                    if ((used_twice & mask0) != 0 || (used_twice & mask1) != 0)
                        ok = 1'b0;
                    if (ok) begin
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
