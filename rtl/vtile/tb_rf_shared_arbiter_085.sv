module tb_rf_shared_arbiter_085;
reg [7:0] rv; reg [15:0] rb; reg [3:0] wv; reg [7:0] wb;
wire [7:0] rg; wire [3:0] wg;
rf_shared_arbiter_085 dut(.rd_valid(rv),.rd_bank(rb),.wr_valid(wv),.wr_bank(wb),.rd_grant(rg),.wr_grant(wg));
initial begin rv=8'hff;rb=16'h0000;wv=4'hf;wb=8'h00;#1;
if (rg !== 8'h03 || wg !== 4'h1) $fatal(1,"grant mismatch");
rv=0;wv=0;#1;if(rg!==0 || wg!==0) $fatal(1,"idle mismatch");
$display("PASS");$finish;end
endmodule
