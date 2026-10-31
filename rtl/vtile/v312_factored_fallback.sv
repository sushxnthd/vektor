// V312 alternative implementation of SAME rejection-aware fallback mechanism.
// One-hot occupancy encoding reduces variable-indexed 2-bit port-count muxes.
// Both read operands are charged, including equal-bank operands.
module vektor_v312_factored_fallback (
    input wire [3:0] primary_valid,
    input wire [3:0] backup_valid,
    input wire [15:0] primary_src0_flat,
    input wire [15:0] primary_src1_flat,
    input wire [15:0] backup_src0_flat,
    input wire [15:0] backup_src1_flat,
    output reg [3:0] issue_valid,
    output reg [3:0] use_backup
);
    reg [15:0] used_once, used_twice;
    reg [15:0] pm0, pm1, bm0, bm1;
    reg [3:0] p0, p1, b0, b1;
    reg pf, bf;
    integer slot;
    always @* begin
        used_once=0; used_twice=0;
        issue_valid=0; use_backup=0;
        pm0=0; pm1=0; bm0=0; bm1=0;
        p0=0; p1=0; b0=0; b1=0;
        pf=0; bf=0;
        for (slot=0;slot<4;slot=slot+1) begin
            p0=(primary_src0_flat >> (4*slot)) & 4'hf;
            p1=(primary_src1_flat >> (4*slot)) & 4'hf;
            b0=(backup_src0_flat >> (4*slot)) & 4'hf;
            b1=(backup_src1_flat >> (4*slot)) & 4'hf;
            pm0=16'h1 << p0; pm1=16'h1 << p1;
            bm0=16'h1 << b0; bm1=16'h1 << b1;
            if (p0==p1) pf=((used_once & pm0)==0);
            else pf=((used_twice & (pm0|pm1))==0);
            if (b0==b1) bf=((used_once & bm0)==0);
            else bf=((used_twice & (bm0|bm1))==0);
            if (primary_valid[slot] && pf) begin
                issue_valid[slot]=1'b1;
                if (p0==p1) used_twice=used_twice | pm0;
                else used_twice=used_twice | (used_once & (pm0|pm1));
                used_once=used_once | pm0 | pm1;
            end else if (backup_valid[slot] && bf) begin
                issue_valid[slot]=1'b1; use_backup[slot]=1'b1;
                if (b0==b1) used_twice=used_twice | bm0;
                else used_twice=used_twice | (used_once & (bm0|bm1));
                used_once=used_once | bm0 | bm1;
            end
        end
    end
endmodule
