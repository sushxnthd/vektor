// Vektor-045: two-source/two-port four-request RF conflict hypergraph.
// Model contract: each operand consumes one bank read; no multicast.
// Standalone combinational research block. No timing, replay or fairness claim.
module vektor_rf_hypergraph_045(
 input wire [1:0] phase,
 input wire [3:0] valid,
 input wire [15:0] src0,
 input wire [15:0] src1,
 output reg [3:0] grant
);
 function automatic pair_bad;
 input [3:0] a,b,c,d;
 begin pair_bad=((a==b)&&((a==c)||(a==d)))||
                ((c==d)&&((c==a)||(c==b))); end
 endfunction
 function automatic triple_bad;
 input [3:0] a,b,c,d,e,f;
 begin triple_bad=(((a==c)||(a==d))&&((a==e)||(a==f)))||
                  (((b==c)||(b==d))&&((b==e)||(b==f))); end
 endfunction
 wire [5:0] p;
 wire [3:0] t;
 assign p[0]=pair_bad(src0[3:0],src1[3:0],src0[7:4],src1[7:4]);
 assign p[1]=pair_bad(src0[3:0],src1[3:0],src0[11:8],src1[11:8]);
 assign p[2]=pair_bad(src0[3:0],src1[3:0],src0[15:12],src1[15:12]);
 assign p[3]=pair_bad(src0[7:4],src1[7:4],src0[11:8],src1[11:8]);
 assign p[4]=pair_bad(src0[7:4],src1[7:4],src0[15:12],src1[15:12]);
 assign p[5]=pair_bad(src0[11:8],src1[11:8],src0[15:12],src1[15:12]);
 assign t[0]=triple_bad(src0[3:0],src1[3:0],src0[7:4],src1[7:4],src0[11:8],src1[11:8]);
 assign t[1]=triple_bad(src0[3:0],src1[3:0],src0[7:4],src1[7:4],src0[15:12],src1[15:12]);
 assign t[2]=triple_bad(src0[3:0],src1[3:0],src0[11:8],src1[11:8],src0[15:12],src1[15:12]);
 assign t[3]=triple_bad(src0[7:4],src1[7:4],src0[11:8],src1[11:8],src0[15:12],src1[15:12]);
 function automatic feasible;
 input [3:0] m;
 input [5:0] pairs;
 input [3:0] triples;
 begin
 feasible=!((m[0]&&m[1]&&pairs[0])||
 (m[0]&&m[2]&&pairs[1])||
 (m[0]&&m[3]&&pairs[2])||
 (m[1]&&m[2]&&pairs[3])||
 (m[1]&&m[3]&&pairs[4])||
 (m[2]&&m[3]&&pairs[5])||
 (m[0]&&m[1]&&m[2]&&triples[0])||
 (m[0]&&m[1]&&m[3]&&triples[1])||
 (m[0]&&m[2]&&m[3]&&triples[2])||
 (m[1]&&m[2]&&m[3]&&triples[3]));
 end
 endfunction
 function automatic integer pop;
 input [3:0] m;
 integer j;
 begin pop=0;for(j=0;j<4;j=j+1)pop=pop+m[j];end
 endfunction
 function automatic integer lex;
 input [3:0] m;
 input [1:0] ph;
 integer j;
 begin lex=0;for(j=0;j<4;j=j+1)lex=(lex<<1)|((m>>((ph+j)&3))&1);end
 endfunction
 integer i,c,rank,best_count,best_rank;
 reg [3:0] m;
 always @* begin
 grant=0;m=0;c=0;rank=0;best_count=-1;best_rank=-1;
 for(i=0;i<16;i=i+1)begin
 m=i[3:0];
 if(((m&valid)==m)&&feasible(m,p,t))begin
 c=pop(m);rank=lex(m,phase);
 if((c>best_count)||((c==best_count)&&(rank>best_rank)))begin
 best_count=c;best_rank=rank;grant=m;
 end
 end
 end
 end
endmodule
