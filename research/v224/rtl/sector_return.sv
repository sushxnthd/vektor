module v224_sector_encode(input wire [127:0] line,output reg [3:0] mask,output reg [127:0] packed,output reg [2:0] payload_count);
integer i,wr;
always @* begin
 mask=0;packed=0;payload_count=0;wr=0;
 for(i=0;i<4;i=i+1) if(line[i*32 +:32]!=0) begin
  mask[i]=1'b1;packed[wr*32 +:32]=line[i*32 +:32];wr=wr+1;
 end
 payload_count=wr[2:0];
end
endmodule
module v224_line_encode(input wire [127:0] line,output wire [3:0] mask,output wire [127:0] packed,output wire [2:0] payload_count);
wire nz=|line;
assign mask=nz?4'b1111:4'b0000;
assign packed=nz?line:128'b0;
assign payload_count=nz?3'd4:3'd0;
endmodule
module v224_decode(input wire [3:0] mask,input wire [127:0] packed,output reg [127:0] line);
integer i,rd;
always @* begin
 line=0;rd=0;
 for(i=0;i<4;i=i+1) if(mask[i]) begin
  line[i*32 +:32]=packed[rd*32 +:32];rd=rd+1;
 end
end
endmodule
