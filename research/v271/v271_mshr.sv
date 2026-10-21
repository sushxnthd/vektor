module v271_mshr #(parameter MODE=1,SPLIT=4,TAGW=16)(
input clk,rst,req_a,req_b,ret_a,ret_b,
input [TAGW-1:0] tag_a,tag_b,
input [2:0] ret_id_a,ret_id_b,
output reg grant_a,grant_b,
output reg [2:0] alloc_id_a,alloc_id_b,
output wire ret_ok_a,ret_ok_b,
output wire [TAGW-1:0] ret_tag_a,ret_tag_b,
output wire [7:0] busy_state);
reg [7:0] busy,owner;
reg [TAGW-1:0] tags[0:7];
reg [7:0] free_mask;
integer i;
wire [7:0] amask=(MODE==0)?((8'h01<<SPLIT)-1):((MODE==1)?8'hc7:8'hff);
wire [7:0] bmask=(MODE==0)?~amask:((MODE==1)?8'hf8:8'hff);
assign ret_ok_a=ret_a&&busy[ret_id_a]&&!owner[ret_id_a];
assign ret_ok_b=ret_b&&busy[ret_id_b]&&owner[ret_id_b]&&!(ret_a&&ret_id_a==ret_id_b);
assign ret_tag_a=tags[ret_id_a];
assign ret_tag_b=tags[ret_id_b];
assign busy_state=busy;
always @* begin
free_mask=~busy;
if(ret_ok_a)free_mask[ret_id_a]=1;
if(ret_ok_b)free_mask[ret_id_b]=1;
grant_a=0;grant_b=0;alloc_id_a=0;alloc_id_b=0;
for(i=0;i<8;i=i+1)
if(req_a&&!grant_a&&free_mask[i]&&amask[i])begin
grant_a=1;alloc_id_a=i;free_mask[i]=0;end
for(i=0;i<8;i=i+1)
if(req_b&&!grant_b&&free_mask[i]&&bmask[i]&&
!(MODE==1&&grant_a&&alloc_id_a>=6&&i>=6))begin
grant_b=1;alloc_id_b=i;free_mask[i]=0;end
end
always @(posedge clk)begin
if(rst)begin busy<=0;owner<=0;end
else begin
if(ret_ok_a)busy[ret_id_a]<=0;
if(ret_ok_b)busy[ret_id_b]<=0;
if(grant_a)begin busy[alloc_id_a]<=1;owner[alloc_id_a]<=0;tags[alloc_id_a]<=tag_a;end
if(grant_b)begin busy[alloc_id_b]<=1;owner[alloc_id_b]<=1;tags[alloc_id_b]<=tag_b;end
end
end
endmodule