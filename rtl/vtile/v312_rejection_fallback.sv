// V312: 4-slot rejection-aware primary/backup RF admission.
// 16 banks, exactly 2 reads per bank per cycle. No extra ports or issue slots.
// Bank IDs are NOT full register IDs: this design conservatively charges both
// operands even if their bank indices match (no unsafe operand coalescing).
module vektor_v312_rejection_fallback (
    input wire [3:0] primary_valid,
    input wire [3:0] backup_valid,
    input wire [15:0] primary_src0_flat,
    input wire [15:0] primary_src1_flat,
    input wire [15:0] backup_src0_flat,
    input wire [15:0] backup_src1_flat,
    output reg [3:0] issue_valid,
    output reg [3:0] use_backup
);
    reg [31:0] used_ports; // 2-bit count per bank: 0, 1, or 2
    integer slot;
    integer p0, p1, b0, b1;
    reg primary_fits, backup_fits;
    always @* begin
        used_ports = 32'b0;
        issue_valid = 4'b0;
        use_backup = 4'b0;
        p0 = 0; p1 = 0; b0 = 0; b1 = 0;
        primary_fits = 1'b0;
        backup_fits = 1'b0;
        for (slot = 0; slot < 4; slot = slot + 1) begin
            p0 = (primary_src0_flat >> (slot*4)) & 15;
            p1 = (primary_src1_flat >> (slot*4)) & 15;
            b0 = (backup_src0_flat >> (slot*4)) & 15;
            b1 = (backup_src1_flat >> (slot*4)) & 15;
            if (p0 == p1)
                primary_fits = (used_ports[2*p0 +: 2] == 2'd0);
            else
                primary_fits = (used_ports[2*p0 +: 2] < 2'd2) &&
                               (used_ports[2*p1 +: 2] < 2'd2);
            if (b0 == b1)
                backup_fits = (used_ports[2*b0 +: 2] == 2'd0);
            else
                backup_fits = (used_ports[2*b0 +: 2] < 2'd2) &&
                              (used_ports[2*b1 +: 2] < 2'd2);

            if (primary_valid[slot] && primary_fits) begin
                issue_valid[slot] = 1'b1;
                if (p0 == p1)
                    used_ports[2*p0 +: 2] = 2'd2;
                else begin
                    used_ports[2*p0 +: 2] = used_ports[2*p0 +: 2] + 2'd1;
                    used_ports[2*p1 +: 2] = used_ports[2*p1 +: 2] + 2'd1;
                end
            end else if (backup_valid[slot] && backup_fits) begin
                issue_valid[slot] = 1'b1;
                use_backup[slot] = 1'b1;
                if (b0 == b1)
                    used_ports[2*b0 +: 2] = 2'd2;
                else begin
                    used_ports[2*b0 +: 2] = used_ports[2*b0 +: 2] + 2'd1;
                    used_ports[2*b1 +: 2] = used_ports[2*b1 +: 2] + 2'd1;
                end
            end
        end
    end
endmodule
