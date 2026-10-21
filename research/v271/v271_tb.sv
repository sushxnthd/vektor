module v271_tb;
parameter integer MODE=1,SPLIT=4;
reg clk=0,rst=1,req_a=0,req_b=0,ret_a=0,ret_b=0;
reg [2:0] ret_id_a=0,ret_id_b=0;
reg [15:0] tag_a=0,tag_b=0;
wire grant_a,grant_b,ret_ok_a,ret_ok_b;
wire [2:0] alloc_id_a,alloc_id_b;
wire [15:0] ret_tag_a,ret_tag_b;
wire [7:0] busy_state;
reg [7:0] expbusy=0,expowner=0;
reg [15:0] exptag[0:7];
integer cyc,i,j,got_a,got_b,grants=0,returns=0;
v271_mshr #(.MODE(MODE),.SPLIT(SPLIT)) dut (.*);
always #5 clk=~clk;
initial begin
@(negedge clk);rst=0;
for(cyc=0;cyc<4000;cyc=cyc+1) begin
@(negedge clk);
ret_a=0;ret_b=0;ret_id_a=0;ret_id_b=0;got_a=-1;got_b=-1;
for(j=0;j<8;j=j+1) begin
i=(j+cyc)%8;
if(expbusy[i] && !expowner[i] && got_a<0) got_a=i;
if(expbusy[i] && expowner[i] && got_b<0) got_b=i;
end
if(got_a>=0 && cyc%3==0) begin ret_a=1;ret_id_a=got_a;end
if(got_b>=0 && cyc%4==0) begin ret_b=1;ret_id_b=got_b;end
req_a=(cyc%7!=0);req_b=(cyc%5!=0);
tag_a=cyc;tag_b=cyc^16'h5a5a;
#1;
if(ret_a && (!ret_ok_a || ret_tag_a!==exptag[ret_id_a])) $fatal(1,"A return mismatch");
if(ret_b && (!ret_ok_b || ret_tag_b!==exptag[ret_id_b])) $fatal(1,"B return mismatch");
if(grant_a && grant_b && alloc_id_a==alloc_id_b) $fatal(1,"double allocate");
if((grant_a && !req_a)||(grant_b && !req_b)) $fatal(1,"spurious grant");
@(posedge clk);
if(ret_a) begin expbusy[ret_id_a]=0;returns=returns+1;end
if(ret_b) begin expbusy[ret_id_b]=0;returns=returns+1;end
if(grant_a) begin expbusy[alloc_id_a]=1;expowner[alloc_id_a]=0;exptag[alloc_id_a]=tag_a;grants=grants+1;end
if(grant_b) begin expbusy[alloc_id_b]=1;expowner[alloc_id_b]=1;exptag[alloc_id_b]=tag_b;grants=grants+1;end
#1;
if(busy_state!==expbusy) $fatal(1,"busy mismatch mode %0d cycle %0d",MODE,cyc);
end
$display("PASS MODE=%0d SPLIT=%0d cycles=4000 grants=%0d returns=%0d",MODE,SPLIT,grants,returns);
$finish;
end
endmodule