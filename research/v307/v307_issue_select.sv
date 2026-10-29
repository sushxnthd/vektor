// V307 5-warp / 8-bank / 3-slot registered selector, matched interfaces.
// MODE=0 MAX-NOW; MODE=1 pressure tie-break; MODE=2 exact FUTURE-TIE.
// This is a combinational decision model, NOT a complete operand collector.
module v307_issue_select #(
    parameter integer MODE = 1
)(
    input wire clk,
    input wire rst_n,
    input wire [4:0] ready,
    input wire [4:0] next_valid,
    input wire [39:0] current_banks,
    input wire [39:0] next_banks,
    output reg [4:0] selected_q
);
    function automatic integer pop5(input reg [4:0] x);
        integer i;
        begin pop5=0; for(i=0;i<5;i=i+1) pop5=pop5+x[i]; end
    endfunction
    function automatic integer rev5(input reg [4:0] x);
        integer i;
        begin rev5=0; for(i=0;i<5;i=i+1) rev5=rev5*2+x[i]; end
    endfunction
    reg [4:0] chosen;
    reg [4:0] s_bits;
    reg [4:0] t_bits;
    reg [4:0] post_ready;
    reg [39:0] post_banks;
    reg [7:0] used;
    reg [7:0] mask;
    reg [7:0] used_next;
    reg [7:0] mask_next;
    integer counts [0:7];
    integer s,t,w,b;
    integer now_count, future_count, pressure, best_now, best_score, score;
    reg ok, ok_next;
    always @* begin
        chosen=0;
        best_now=-1;
        best_score=-100000;
        s_bits=0; t_bits=0; post_ready=0; post_banks=0;
        used=0; mask=0; used_next=0; mask_next=0;
        now_count=0; future_count=0; pressure=0; score=0;
        ok=0; ok_next=0;
        for(b=0;b<8;b=b+1) counts[b]=0;
        for(s=0;s<32;s=s+1) begin
            s_bits=s[4:0];
            now_count=pop5(s_bits);
            ok=(now_count<=3);
            used=0;
            for(w=0;w<5;w=w+1) begin
                mask=current_banks[w*8+:8];
                if(s_bits[w]) begin
                    if(!ready[w] || ((used & mask)!=0)) ok=0;
                    used=used | mask;
                end
            end
            if(ok) begin
                post_ready=0;
                post_banks=0;
                for(w=0;w<5;w=w+1) begin
                    if(s_bits[w]) begin
                        post_ready[w]=next_valid[w];
                        post_banks[w*8+:8]=next_banks[w*8+:8];
                    end else begin
                        post_ready[w]=ready[w];
                        post_banks[w*8+:8]=current_banks[w*8+:8];
                    end
                end
                pressure=0;
                for(b=0;b<8;b=b+1) begin
                    counts[b]=0;
                    for(w=0;w<5;w=w+1) begin
                        if(post_ready[w] && post_banks[w*8+b]) counts[b]=counts[b]+1;
                    end
                    if(counts[b]>1) pressure=pressure+counts[b]-1;
                end
                future_count=0;
                if(MODE==2) begin
                    for(t=0;t<32;t=t+1) begin
                        t_bits=t[4:0];
                        ok_next=(pop5(t_bits)<=3);
                        used_next=0;
                        for(w=0;w<5;w=w+1) begin
                            mask_next=post_banks[w*8+:8];
                            if(t_bits[w]) begin
                                if(!post_ready[w] || ((used_next & mask_next)!=0)) ok_next=0;
                                used_next=used_next | mask_next;
                            end
                        end
                        if(ok_next && pop5(t_bits)>future_count) future_count=pop5(t_bits);
                    end
                end
                if(MODE==1) score=-pressure;
                else if(MODE==2) score=future_count;
                else score=0;
                if(now_count>best_now ||
                   (now_count==best_now && (score>best_score ||
                   (score==best_score && rev5(s_bits)>rev5(chosen))))) begin
                    chosen=s_bits;
                    best_now=now_count;
                    best_score=score;
                end
            end
        end
    end
    always @(posedge clk or negedge rst_n) begin
        if(!rst_n) selected_q<=0;
        else selected_q<=chosen;
    end
endmodule
