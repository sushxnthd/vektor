module v268_sector_rf #(parameter int WORDS=16,parameter int DW=32,parameter int AW=$clog2(WORDS))(
 input logic clk,rd_en,input logic [AW-1:0] rd_addr,
 input logic [31:0] rd_mask,output logic [32*DW-1:0] rd_data,
 input logic wr_en,input logic [AW-1:0] wr_addr,
 input logic [31:0] wr_mask,input logic [32*DW-1:0] wr_data
);
 logic [8*DW-1:0] sector_mem [0:3][0:WORDS-1];
 logic [8*DW-1:0] sector_q [0:3];
 logic [31:0] rd_mask_q;
 always_ff @(posedge clk) begin
  rd_mask_q <= rd_en ? rd_mask : '0;
  for(int s=0;s<4;s++) begin
   if(wr_en)
    for(int l=0;l<8;l++)
     if(wr_mask[8*s+l])
      sector_mem[s][wr_addr][DW*l +: DW]<=wr_data[DW*(8*s+l)+:DW];
   if(rd_en && (|rd_mask[8*s+:8]))
    sector_q[s]<=sector_mem[s][rd_addr];
  end
 end
 always_comb begin
  rd_data='0;
  for(int s=0;s<4;s++)
   for(int l=0;l<8;l++)
    if(rd_mask_q[8*s+l])
     rd_data[DW*(8*s+l)+:DW]=sector_q[s][DW*l+:DW];
 end
endmodule
