module tb_lookup;
reg [383:0] tags;
reg [15:0] valid;
reg [23:0] query;
wire global_hit,banked_hit;
integer t,i,bank,slot,used[0:3];
reg [23:0] tag;
v221_global_lookup g(.tags(tags),.valid(valid),.query(query),.hit(global_hit));
v221_banked_lookup b(.tags(tags),.valid(valid),.query(query),.hit(banked_hit));
initial begin
for(t=0;t<5000;t=t+1) begin
tags=0;valid=0;
for(i=0;i<4;i=i+1) used[i]=0;
for(i=0;i<16;i=i+1) begin
tag=$random & 24'hffffff;bank=tag&3;
if(used[bank]<4 && (($random&3)!=0)) begin
slot=bank*4+used[bank];used[bank]=used[bank]+1;
tags[slot*24 +: 24]=tag;valid[slot]=1'b1;
end
end
query=$random & 24'hffffff;
if(valid[t%16]) query=tags[(t%16)*24 +: 24];
#1;
if(global_hit !== banked_hit) begin
$display("FAIL t=%0d query=%h global=%b banked=%b",t,query,global_hit,banked_hit);
$fatal(1);
end
end
$display("PASS 5000 differential lookups");$finish;
end
endmodule
