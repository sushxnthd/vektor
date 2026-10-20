module v243_final_select(
input wire [3:0] valid,
input wire [3:0] final_fragment,
output wire [3:0] grant
);
wire [3:0] eligible=valid & final_fragment;
wire [3:0] selected=(|eligible) ? eligible : valid;
assign grant[0]=selected[0];
assign grant[1]=selected[1] & ~selected[0];
assign grant[2]=selected[2] & ~(|selected[1:0]);
assign grant[3]=selected[3] & ~(|selected[2:0]);
endmodule
