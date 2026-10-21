// V268 matched full-width control: same capacity and 1R1W.
module v268_fullwidth_control #(parameter int WORDS=16,DW=32,AW=$clog2(WORDS))(
 input logic clk,rd_en,wr_en,
 input logic [AW-1:0] rd_addr,wr_addr,
 input logic [31:0] rd_mask,wr_mask,
 input logic [32*DW-1:0] wr_data,
 output logic [32*DW-1:0] rd_data);
 logic [32*DW-1:0] mem[0:WORDS-1],q;
 logic [31:0] mask_q;
 always_ff @(posedge clk) begin
  mask_q <= rd_en ? rd_mask : '0;
  if (wr_en)
   for (int l=0;l<32;l++)
    if (wr_mask[l])
     mem[wr_addr][DW*l +: DW] <= wr_data[DW*l +: DW];
  if (rd_en) q <= mem[rd_addr];
 end
 always_comb begin
  rd_data='0;
  for (int l=0;l<32;l++)
   if (mask_q[l]) rd_data[DW*l +: DW] = q[DW*l +: DW];
 end
endmodule
