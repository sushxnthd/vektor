// Vektor-094 source-side nonfinal return coalescer.
// Requires exact expected source beat count and producer quiescence
// before tag reuse. Not a complete return-network implementation.
module wb_return_coalescer_094 #(
 parameter integer TAG_BITS=3,COUNT_BITS=4
)(
 input wire clk,rst_n,req_valid,
 output wire req_ready,
 input wire [TAG_BITS-1:0] req_tag,
 input wire [COUNT_BITS-1:0] expected_beats,
 input wire source_beat_valid,
 output wire ret_valid,
 input wire ret_ready,
 output wire [TAG_BITS-1:0] ret_tag,
 output wire ret_final
);
 reg busy,final_pending;
 reg [TAG_BITS-1:0] tag;
 reg [COUNT_BITS-1:0] remaining;
 assign req_ready=!busy;
 assign ret_valid=busy&&final_pending;
 assign ret_tag=tag;
 assign ret_final=ret_valid;
 always @(posedge clk or negedge rst_n) begin
  if(!rst_n) begin busy<=0;final_pending<=0;tag<=0;remaining<=0;end
  else if(!busy) begin
   if(req_valid && expected_beats!=0) begin
    busy<=1;final_pending<=0;tag<=req_tag;remaining<=expected_beats;
   end
  end else if(final_pending) begin
   if(ret_ready) begin busy<=0;final_pending<=0;remaining<=0;end
  end else if(source_beat_valid) begin
   if(remaining==1) begin remaining<=0;final_pending<=1;end
   else remaining<=remaining-1'b1;
  end
 end
endmodule
