module tb_v293;
reg clk=0, rst=1, req_valid=1, wr_en=0;
reg [7:0] req_addr=0, wr_addr=0;
reg [31:0] rf_data=0, wr_data=0;
wire vl,vg,rl,rg,hl,hg;
wire [31:0] dl,dg;
integer i;
v293_bypass #(.LOCAL(1)) a(clk,rst,req_valid,req_addr,rf_data,wr_en,wr_addr,wr_data,vl,dl,rl,hl);
v293_bypass #(.LOCAL(0)) b(clk,rst,req_valid,req_addr,rf_data,wr_en,wr_addr,wr_data,vg,dg,rg,hg);
initial begin
#2; clk=1; #2; clk=0; rst=0;
for(i=0;i<4096;i=i+1) begin
 req_addr=i%16; rf_data=32'hcafebabe ^ req_addr;
 #1;
 if(dl !== rf_data || dg !== rf_data) $fatal(1,"data mismatch");
 clk=1; #1; clk=0;
end
$display("PASS 4096 deterministic cycles"); $finish;
end
endmodule
