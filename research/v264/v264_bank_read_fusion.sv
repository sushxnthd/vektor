// Exploratory 1R bank / two-destination adapter, not STA qualified.
// Same exact netlist for candidate and strongest matched broadcast control.
module v264_bank_read_fusion #(
 parameter ADDR_W=12, ID_W=24, DATA_W=32
)(
 input wire clk,rst_n,req0_valid,req1_valid,bank_read_ready,bank_wr_valid,
 input wire [ID_W-1:0] req0_id,req1_id,
 input wire [ADDR_W-1:0] req0_addr,req1_addr,bank_wr_addr,
 input wire [DATA_W-1:0] bank_rd_data,
 output wire grant0,grant1,bank_rd_en,
 output wire [ADDR_W-1:0] bank_rd_addr,
 output reg resp0_valid,resp1_valid,
 output wire [DATA_W-1:0] resp0_data,resp1_data
);
 wire same = req0_valid && req1_valid && (req0_id==req1_id) && (req0_addr==req1_addr);
 assign bank_rd_addr=req0_valid?req0_addr:req1_addr;
 wire fire=bank_read_ready && !(bank_wr_valid && bank_wr_addr==bank_rd_addr);
 assign grant0=req0_valid && fire;
 assign grant1=req1_valid && fire && (!req0_valid || same);
 assign bank_rd_en=grant0 || grant1;
 always @(posedge clk or negedge rst_n) begin
   if(!rst_n) begin resp0_valid<=0;resp1_valid<=0;end
   else begin resp0_valid<=grant0;resp1_valid<=grant1;end
 end
 assign resp0_data=bank_rd_data;
 assign resp1_data=bank_rd_data;
endmodule
module v264_matched_broadcast #(
 parameter ADDR_W=12,ID_W=24,DATA_W=32
)(
 input wire clk,rst_n,req0_valid,req1_valid,bank_read_ready,bank_wr_valid,
 input wire [ID_W-1:0] req0_id,req1_id,
 input wire [ADDR_W-1:0] req0_addr,req1_addr,bank_wr_addr,
 input wire [DATA_W-1:0] bank_rd_data,
 output wire grant0,grant1,bank_rd_en,
 output wire [ADDR_W-1:0] bank_rd_addr,
 output wire resp0_valid,resp1_valid,
 output wire [DATA_W-1:0] resp0_data,resp1_data
);
 v264_bank_read_fusion #(.ADDR_W(ADDR_W),.ID_W(ID_W),.DATA_W(DATA_W)) u(
 .clk(clk),.rst_n(rst_n),.req0_valid(req0_valid),.req1_valid(req1_valid),
 .bank_read_ready(bank_read_ready),.bank_wr_valid(bank_wr_valid),
 .req0_id(req0_id),.req1_id(req1_id),.req0_addr(req0_addr),.req1_addr(req1_addr),
 .bank_wr_addr(bank_wr_addr),.bank_rd_data(bank_rd_data),
 .grant0(grant0),.grant1(grant1),.bank_rd_en(bank_rd_en),.bank_rd_addr(bank_rd_addr),
 .resp0_valid(resp0_valid),.resp1_valid(resp1_valid),.resp0_data(resp0_data),.resp1_data(resp1_data));
endmodule
