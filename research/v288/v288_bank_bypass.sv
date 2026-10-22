// V288 first-stage admission only; E0 hypothesis, NOT a complete RF.
// Four requests share two physical RF read ports; a matching forwarded producer
// bypasses both ports. Address equality is FULL physical address equality.
module v288_bank_bypass #(
 parameter AW=12, W=32
)(
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
 integer i;
 reg hit;
 always @* begin
   grant=4'b0; forwarded=4'b0; read_count=2'b0; hit=1'b0;
   for(i=0;i<4;i=i+1) begin
     hit = bypass_valid && (req_addr[i*AW+:AW] == bypass_addr);
     if(req_valid[i]) begin
       if(hit) begin grant[i]=1'b1; forwarded[i]=1'b1; end
       else if(read_count < 2) begin grant[i]=1'b1; read_count=read_count+1'b1; end
     end
   end
 end
 genvar j;
 generate for(j=0;j<4;j=j+1) begin: fw
   assign forwarded_data[j*W+:W]=forwarded[j] ? bypass_data : {W{1'b0}};
 end endgenerate
endmodule
