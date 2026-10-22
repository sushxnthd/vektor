// One-word, one-bit second-chance control; identical RF and data/tag capacity.
module v277_onebit(
 input wire clk,rst,req_valid,
 input wire [7:0] req_tag,
 input wire [31:0] rf_data,
 input wire invalidate,
 input wire [7:0] inv_tag,
 output wire hit,rf_read,
 output wire [31:0] out_data
);
reg valid;
reg [7:0] tag;
reg [31:0] data;
reg protected;
wire invalidating=invalidate && valid && (inv_tag==tag);
wire match_tag=valid && !invalidating && (tag==req_tag);
assign hit=req_valid && match_tag;
assign rf_read=req_valid && !match_tag;
assign out_data=hit ? data : rf_data;
always @(posedge clk) begin
 if(rst) begin valid<=0;tag<=0;data<=0;protected<=0;end
 else if(invalidating) begin valid<=0;protected<=0;end
 else if(req_valid) begin
  if(match_tag) protected<=1;
  else if(protected) protected<=0;
  else begin valid<=1;tag<=req_tag;data<=rf_data;protected<=0;end
 end
end
endmodule
