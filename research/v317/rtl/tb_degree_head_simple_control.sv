// Independent, enumeration-based functional reference; does not use DUT sorting network.
// Exhaustive 2-bank operand patterns * all valid masks; two frozen 3-bank witnesses.
module tb_v317_degree_head;
    reg [3:0] request_valid;
    reg [15:0] src0_bank_flat, src1_bank_flat;
    wire [3:0] degree_grant, greedy_grant;
    integer aa[0:3], bb[0:3], deg[0:3], order[0:3];
    integer valid_id, pattern, i, j, k, bank, demand, temp, cases;
    integer degree_total, greedy_total, degree_wins, degree_losses;
    reg [3:0] expected, candidate;
    reg allowed;

    vektor_v317_degree_head_arbiter dut(
        .request_valid(request_valid),.src0_bank_flat(src0_bank_flat),
        .src1_bank_flat(src1_bank_flat),.grant(degree_grant)
    );
    vektor_v309_compact_greedy_arbiter baseline(
        .request_valid(request_valid),.src0_bank_flat(src0_bank_flat),
        .src1_bank_flat(src1_bank_flat),.grant(greedy_grant)
    );

    function integer popcount;
        input [3:0] m;
        integer bit_id;
        begin
            popcount=0;
            for(bit_id=0;bit_id<4;bit_id=bit_id+1)
                if(m[bit_id])popcount=popcount+1;
        end
    endfunction

    task check_case;
        begin
            #1;
            for(i=0;i<4;i=i+1) begin
                aa[i]=src0_bank_flat[i*4 +:4];
                bb[i]=src1_bank_flat[i*4 +:4];
                deg[i]=0;
                order[i]=i;
            end
            for(i=0;i<4;i=i+1)
                for(j=0;j<4;j=j+1)
                    if(i!=j && request_valid[j] &&
                       (aa[i]==aa[j] || aa[i]==bb[j] ||
                        bb[i]==aa[j] || bb[i]==bb[j]))
                        deg[i]=deg[i]+1;
            for(i=1;i<4;i=i+1)
                for(j=i+1;j<4;j=j+1)
                    if(deg[order[j]]<deg[order[i]] ||
                       (deg[order[j]]==deg[order[i]] && order[j]<order[i])) begin
                        temp=order[i];order[i]=order[j];order[j]=temp;
                    end
            expected=4'b0000;
            for(i=0;i<4;i=i+1) begin
                if(request_valid[order[i]]) begin
                    candidate=expected | (4'b0001 << order[i]);
                    allowed=1'b1;
                    for(bank=0;bank<16;bank=bank+1) begin
                        demand=0;
                        for(k=0;k<4;k=k+1) begin
                            if(candidate[k]) begin
                                if(aa[k]==bank)demand=demand+1;
                                if(bb[k]==bank)demand=demand+1;
                            end
                        end
                        if(demand>2)allowed=1'b0;
                    end
                    if(allowed)expected=candidate;
                end
            end
            if(degree_grant !== expected)
                $fatal(1,"degree mismatch valid=%h a=%h b=%h got=%h expected=%h",
                    request_valid,src0_bank_flat,src1_bank_flat,degree_grant,expected);
            if(degree_grant & ~request_valid)
                $fatal(1,"invalid grant");
            if(request_valid[0] && !degree_grant[0])
                $fatal(1,"oldest request skipped");
            cases=cases+1;
            degree_total=degree_total+popcount(degree_grant);
            greedy_total=greedy_total+popcount(greedy_grant);
            if(popcount(degree_grant)>popcount(greedy_grant))degree_wins=degree_wins+1;
            if(popcount(degree_grant)<popcount(greedy_grant))degree_losses=degree_losses+1;
        end
    endtask

    initial begin
        request_valid=0;src0_bank_flat=0;src1_bank_flat=0;
        cases=0;degree_total=0;greedy_total=0;degree_wins=0;degree_losses=0;
        for(valid_id=0;valid_id<16;valid_id=valid_id+1)
            for(pattern=0;pattern<256;pattern=pattern+1) begin
                request_valid=valid_id[3:0];
                src0_bank_flat=0;src1_bank_flat=0;
                for(k=0;k<4;k=k+1) begin
                    src0_bank_flat[4*k +:4]=(pattern >> (2*k)) & 1;
                    src1_bank_flat[4*k +:4]=(pattern >> (2*k+1)) & 1;
                end
                check_case();
            end
        if(cases!=4096 || degree_total!=5226 || greedy_total!=5210 ||
           degree_wins!=16 || degree_losses!=0)
            $fatal(1,"2-bank totals cases=%0d degree=%0d greedy=%0d wins=%0d losses=%0d",
                cases,degree_total,greedy_total,degree_wins,degree_losses);

        // Frozen 3-bank win: valid 1110, (0,0),(0,1),(0,0),(1,1).
        request_valid=4'b1110;
        src0_bank_flat=16'h1000;src1_bank_flat=16'h1000;
        // slot1 src1=1
        src1_bank_flat[7:4]=4'd1;
        check_case();
        if(greedy_grant!==4'b0010 || degree_grant!==4'b1100)
            $fatal(1,"frozen degree-win witness failed");

        // Frozen 3-bank loss: (0,1),(0,2),(1,2),(2,2).
        request_valid=4'b1111;
        src0_bank_flat=16'h2100;src1_bank_flat=16'h2221;
        check_case();
        if(greedy_grant!==4'b0111 || degree_grant!==4'b1001)
            $fatal(1,"frozen degree-loss witness failed");

        $display("PASS degree RTL: 4096 exhaustive 2-bank valid/pair cases; 2 witnesses");
        $display("2-bank totals: degree=5226 greedy=5210 wins=16 losses=0");
        $finish;
    end
endmodule
