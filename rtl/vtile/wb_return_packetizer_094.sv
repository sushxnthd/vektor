// Vektor-094 single-transaction return packetizer.
// Exactly one FINAL handshake per request if downstream eventually ready.
// Cold reset requires external downstream flush; soft reset must retain state.
module wb_return_packetizer_094 #(
 parameter integer TAG_BITS=3, COPIES_BITS=4
)(
 input wire clk,rst_n,req_valid,
 output wire req_ready,
 input wire [TAG_BITS-1:0] req_tag,
 input wire [COPIES_BITS-1:0] req_copies,
 output wire ret_valid,
 input wire ret_ready,
 output wire [TAG_BITS-1:0] ret_tag,
 output wire ret_final
);
 reg busy;
 reg [TAG_BITS-1:0] tag;
 reg [COPIES_BITS-1:0] remaining;
 assign req_ready=!busy;
 assign ret_valid=busy;
 assign ret_tag=tag;
 assign ret_final=busy && remaining==1;
 always @(posedge clk or negedge rst_n) begin
  if(!rst_n) begin busy<=0;tag<=0;remaining<=0;end
  else if(!busy) begin
   if(req_valid && req_copies!=0) begin
    busy<=1;tag<=req_tag;remaining<=req_copies;
   end
  end else if(ret_ready) begin
   if(remaining==1) begin busy<=0;remaining<=0;end
   else remaining<=remaining-1'b1;
  end
 end
endmodule
