// Vektor-111 scoped byte hazard, abstract SC primitive (not full memory model).
module scoped_byte_hazard #(parameter CTA_W=16, TID_W=32)(
 input wire [63:0] a_addr,b_addr,
 input wire [4:0] a_size,b_size,
 input wire [1:0] a_space,b_space,
 input wire [CTA_W-1:0] a_cta,b_cta,
 input wire [TID_W-1:0] a_tid,b_tid,
 input wire a_write,b_write,
 output wire a_valid,b_valid,hazard
);
 localparam [64:0] LIMIT=65'h10000000000000000;
 wire [64:0] a_end={1'b0,a_addr}+{60'b0,a_size};
 wire [64:0] b_end={1'b0,b_addr}+{60'b0,b_size};
 wire asize=(a_size==1||a_size==2||a_size==4||a_size==8||a_size==16);
 wire bsize=(b_size==1||b_size==2||b_size==4||b_size==8||b_size==16);
 assign a_valid=asize&&(a_space!=3)&&(a_end<=LIMIT);
 assign b_valid=bsize&&(b_space!=3)&&(b_end<=LIMIT);
 wire same=(a_space==b_space)&&((a_space==0)||
  (a_space==1&&a_cta==b_cta)||(a_space==2&&a_tid==b_tid));
 wire overlap=({1'b0,a_addr}<b_end)&&({1'b0,b_addr}<a_end);
 assign hazard=a_valid&&b_valid&&same&&overlap&&(a_write||b_write);
endmodule
