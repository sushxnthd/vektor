module v221_global_lookup(input wire [383:0] tags,input wire [15:0] valid,input wire [23:0] query,output wire hit);
wire [15:0] matches;
genvar i;
generate for(i=0;i<16;i=i+1) begin: g
assign matches[i]=valid[i] && (tags[i*24 +: 24]==query);
end endgenerate
assign hit=|matches;
endmodule

module v221_banked_lookup(input wire [383:0] tags,input wire [15:0] valid,input wire [23:0] query,output wire hit);
wire [1:0] bank=query[1:0];
reg [95:0] selected_tags;
reg [3:0] selected_valid;
always @* begin
case(bank)
2'd0: begin selected_tags=tags[95:0];selected_valid=valid[3:0];end
2'd1: begin selected_tags=tags[191:96];selected_valid=valid[7:4];end
2'd2: begin selected_tags=tags[287:192];selected_valid=valid[11:8];end
default: begin selected_tags=tags[383:288];selected_valid=valid[15:12];end
endcase
end
wire [3:0] matches;
genvar i;
generate for(i=0;i<4;i=i+1) begin: b
assign matches[i]=selected_valid[i] && (selected_tags[i*24 +: 24]==query);
end endgenerate
assign hit=|matches;
endmodule
