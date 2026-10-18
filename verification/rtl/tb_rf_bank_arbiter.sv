module tb_rf_bank_arbiter;
    reg [3:0] request_valid;
    reg [15:0] src0_bank_flat, src1_bank_flat;
    reg [3:0] src_alias;
    wire [3:0] grant;
    integer t, slot, bank, a, b, occ [0:15];
    reg [3:0] oracle;
    reg can_grant;
    vektor_rf_bank_arbiter dut (
        .request_valid(request_valid), .src0_bank_flat(src0_bank_flat),
        .src1_bank_flat(src1_bank_flat), .src_alias(src_alias), .grant(grant)
    );
    task check;
        begin
            for (bank=0;bank<16;bank=bank+1) occ[bank]=0;
            oracle=0;
            for (slot=0;slot<4;slot=slot+1) begin
                a=(src0_bank_flat >> (4*slot)) & 15;
                b=(src1_bank_flat >> (4*slot)) & 15;
                if (request_valid[slot]) begin
                    if (a==b && src_alias[slot])
                        can_grant=(occ[a]<2);
                    else if (a==b)
                        can_grant=(occ[a]==0);
                    else
                        can_grant=(occ[a]<2 && occ[b]<2);
                    if (can_grant) begin
                        oracle[slot]=1;
                        if (a==b && src_alias[slot]) occ[a]=occ[a]+1;
                        else if (a==b) occ[a]=occ[a]+2;
                        else begin occ[a]=occ[a]+1; occ[b]=occ[b]+1; end
                    end
                end
            end
            #1;
            if (grant !== oracle) $fatal(1,"V203 mismatch expected=%b actual=%b",oracle,grant);
            for (bank=0;bank<16;bank=bank+1)
                if (occ[bank]>2) $fatal(1,"V203 bank overbook %0d",bank);
        end
    endtask
    initial begin
        request_valid=4'b1111;
        src0_bank_flat=16'h0000;
        src1_bank_flat=16'h0000;
        src_alias=4'b1111;
        check();
        if (grant!==4'b0011) $fatal(1,"V203 expected two aliased grants");
        src_alias=4'b0000;
        check();
        if (grant!==4'b0001) $fatal(1,"V203 baseline same-bank two-read mismatch");
        for (t=0;t<20000;t=t+1) begin
            request_valid=$random;
            src0_bank_flat=$random;
            src1_bank_flat=$random;
            src_alias=$random;
            check();
        end
        $display("V203 RTL alias arbiter: 20002 checks passed");
        $finish;
    end
endmodule
