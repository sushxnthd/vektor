// Same-resource conventional one-entry operand-cache control, independent RTL formulation.
// Cache entry contains the same tag/data/valid as the proposed forwarding slot.
module v288_operand_cache_control #(parameter AW=12, W=32)(
 input wire [3:0] req_valid,
 input wire [4*AW-1:0] req_addr,
 input wire bypass_valid,
 input wire [AW-1:0] bypass_addr,
 input wire [W-1:0] bypass_data,
 output reg [3:0] grant,
 output reg [3:0] forwarded,
 output wire [4*W-1:0] forwarded_data,
 output reg [1:0] read_count
);
 wire [3:0] cache_hit;
 genvar j;
 generate for(j=0;j<4;j=j+1) begin: h
   assign cache_hit[j] = req_valid[j] && bypass_valid &&
                         (req_addr[j*AW+:AW] == bypass_addr);
   assign forwarded_data[j*W+:W] = forwarded[j] ? bypass_data : {W{1'b0}};
 end endgenerate
 integer i;
 always @* begin
   grant = cache_hit;
   forwarded = cache_hit;
   read_count = 2'b00;
   for(i=0;i<4;i=i+1) begin
     if(req_valid[i] && !cache_hit[i] && read_count < 2) begin
       grant[i] = 1'b1;
       read_count = read_count + 1'b1;
     end
   end
 end
endmodule
