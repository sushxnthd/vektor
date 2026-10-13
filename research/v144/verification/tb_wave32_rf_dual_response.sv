module tb_wave32_rf_dual_response;
reg [17:0] src_regs=0;
reg [2:0] missing=3'b111;
reg [1:0] rf_rsp_valid=2'b11;
reg [11:0] rf_rsp_reg=12'h041;
reg [7:0] rf_rsp_bank=8'h21;
reg [2047:0] rf_rsp_data=0;
wire [1:0] rf_rsp_accept;
wire [2:0] src_rsp_valid;
wire [3071:0] src_rsp_data;
vektor_wave32_rf_dual_response dut(.src_regs(src_regs),.missing(missing),.rf_rsp_valid(rf_rsp_valid),.rf_rsp_reg(rf_rsp_reg),.rf_rsp_bank(rf_rsp_bank),.rf_rsp_data(rf_rsp_data),.rf_rsp_accept(rf_rsp_accept),.src_rsp_valid(src_rsp_valid),.src_rsp_data(src_rsp_data));
initial begin
 #1;
 if(rf_rsp_accept!==2'b11) $fatal(1,"bank independence");
 rf_rsp_bank=8'h11;
 #1;
 if(rf_rsp_accept!==2'b01) $fatal(1,"bank conflict");
 $finish;
end
endmodule
