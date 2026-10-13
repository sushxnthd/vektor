// V143 combinational RF duplicate-read coalescer; not a complete collector.
// Source tags and allocation MUST remain stable through RF response.
// Response source-slot tags identify the accepted physical RF read.
module vektor_wave32_rf_read_coalescer #(
 parameter integer LANES=32, parameter integer REG_BITS=6
)(
 input wire [3*REG_BITS-1:0] src_regs,
 input wire [2:0] missing,
 input wire req_valid,
 output reg [2:0] rf_req,
 input wire [2:0] rf_rsp_valid,
 input wire [3*LANES*32-1:0] rf_rsp_data,
 output reg [2:0] src_rsp_valid,
 output reg [3*LANES*32-1:0] src_rsp_data
);
 localparam integer WIDTH=LANES*32;
 integer i,j;
 reg duplicate;
 always @* begin
   rf_req=3'b000;
   for(i=0;i<3;i=i+1) begin
     duplicate=1'b0;
     for(j=0;j<i;j=j+1)
       if(missing[j] && src_regs[i*REG_BITS +: REG_BITS]==src_regs[j*REG_BITS +: REG_BITS])
         duplicate=1'b1;
     if(req_valid && missing[i] && !duplicate) rf_req[i]=1'b1;
   end
 end
 always @* begin
   src_rsp_valid=3'b000;
   src_rsp_data={3*WIDTH{1'b0}};
   for(i=0;i<3;i=i+1)
     for(j=0;j<3;j=j+1)
       if(missing[i] && !src_rsp_valid[i] && rf_rsp_valid[j] &&
          src_regs[i*REG_BITS +: REG_BITS]==src_regs[j*REG_BITS +: REG_BITS]) begin
         src_rsp_valid[i]=1'b1;
         src_rsp_data[i*WIDTH +: WIDTH]=rf_rsp_data[j*WIDTH +: WIDTH];
       end
 end
endmodule
