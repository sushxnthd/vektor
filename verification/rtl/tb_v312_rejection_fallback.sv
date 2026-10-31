`timescale 1ns/1ps
module tb_v312_rejection_fallback;
    reg [3:0] primary_valid, backup_valid;
    reg [15:0] primary_src0_flat, primary_src1_flat;
    reg [15:0] backup_src0_flat, backup_src1_flat;
    wire [3:0] issue_valid, use_backup;
    integer used[0:15];
    integer t, i, a, b, c, d, k, pf, bf;
    reg [3:0] expected_issue, expected_backup;
    integer accepted;
    vektor_v312_rejection_fallback dut(
        .primary_valid(primary_valid), .backup_valid(backup_valid),
        .primary_src0_flat(primary_src0_flat), .primary_src1_flat(primary_src1_flat),
        .backup_src0_flat(backup_src0_flat), .backup_src1_flat(backup_src1_flat),
        .issue_valid(issue_valid), .use_backup(use_backup)
    );
    task check;
        begin
            for (k=0;k<16;k=k+1) used[k]=0;
            expected_issue=0; expected_backup=0;
            for (i=0;i<4;i=i+1) begin
                a=(primary_src0_flat >> (4*i)) & 15;
                b=(primary_src1_flat >> (4*i)) & 15;
                c=(backup_src0_flat >> (4*i)) & 15;
                d=(backup_src1_flat >> (4*i)) & 15;
                pf=(a==b) ? (used[a]==0) : (used[a]<2 && used[b]<2);
                bf=(c==d) ? (used[c]==0) : (used[c]<2 && used[d]<2);
                if (primary_valid[i] && pf) begin
                    expected_issue[i]=1;
                    used[a]=used[a]+1; used[b]=used[b]+1;
                end else if (backup_valid[i] && bf) begin
                    expected_issue[i]=1; expected_backup[i]=1;
                    used[c]=used[c]+1; used[d]=used[d]+1;
                end
            end
            #1;
            if (issue_valid !== expected_issue || use_backup !== expected_backup) begin
                $display("FAIL t=%0d issue=%b expected=%b backup=%b expected=%b",t,issue_valid,expected_issue,use_backup,expected_backup);
                $fatal(1);
            end
            for (k=0;k<16;k=k+1)
                if (used[k]>2) $fatal(1,"Port overflow bank=%0d",k);
        end
    endtask
    initial begin
        // Frozen hotspot: 2 primaries, 2 fallback grants when all backups ready.
        primary_valid=4'b1111; backup_valid=4'b1111;
        primary_src0_flat=16'h0000; primary_src1_flat=16'h1111;
        backup_src0_flat=16'h8642; backup_src1_flat=16'h9753;
        t=0; check();
        if (issue_valid!==4'b1111 || use_backup!==4'b1100)
            $fatal(1,"Hotspot frozen vector failed");
        // Frozen disjoint: all four primaries, no backups.
        primary_src0_flat=16'h6420; primary_src1_flat=16'h7531;
        backup_src0_flat=16'hECA8; backup_src1_flat=16'hFDB9;
        t=1; check();
        if (issue_valid!==4'b1111 || use_backup!==4'b0000)
            $fatal(1,"Disjoint frozen vector failed");
        // Randomized independent software port-count oracle, including same-bank operands.
        for (t=2;t<50002;t=t+1) begin
            primary_valid=$random; backup_valid=$random;
            primary_src0_flat=$random; primary_src1_flat=$random;
            backup_src0_flat=$random; backup_src1_flat=$random;
            check();
        end
        $display("PASS V312: 50002 independent RTL oracle vectors, bank-port safety");
        $finish;
    end
endmodule
